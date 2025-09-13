from django.http import HttpResponseForbidden
import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from .forms import UploadFileForm
from .models import SalaryStatement
from accounts.models import CustomUser
from datetime import datetime
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import SalaryStatementSerializer
from rest_framework import status
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.urls import reverse_lazy

from .models import SalaryStatement
from tokens.models import ExpiringToken
from .serializers import SalaryStatementSerializer

class MySalaryStatements(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        slips = SalaryStatement.objects.filter(user=request.user).order_by('-month')
        if slips.exists():
            serializer = SalaryStatementSerializer(slips, many=True)
            return Response(serializer.data[0])
        else:
            return Response({'message':[ 'لم يتم رفع مفردات مرتب هذا الشهر بعد']},
                            status=status.HTTP_400_BAD_REQUEST)

# -- أدوات مساعدة: تنسيق رقم الحساب + تحويل رقم عشري --
from decimal import Decimal, InvalidOperation
def normalize_bank_account(value):
    if value is None:
        return ''
    s = str(value).strip()
    for ch in [' ', '\u00A0', '\u200f', '\u200e', '\u202a', '\u202b', '\u202c']:
        s = s.replace(ch, '')
    s = s.translate(str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789'))
    return s

def to_decimal(v):
    if v is None:
        return None
    try:
        s = str(v).strip().replace(',', '')
        if s == '':
            return None
        d = Decimal(s)
        if d < 0:
            return None
        return d
    except (InvalidOperation, ValueError):
        return None

from .models import ExcelUploadLog

# =============== رفع بــ Progress حقيقي ===============
import os, uuid, threading, tempfile
from django.core.cache import cache
from django.http import JsonResponse, HttpResponseBadRequest
from django.db import transaction

_PROGRESS_TTL = 60 * 60  # ثانية (ساعة)

def _progress_key(upload_id: str) -> str:
    return f"salary_upload:{upload_id}"

def _set_progress(upload_id: str, **data):
    key = _progress_key(upload_id)
    state = cache.get(key) or {}
    state.update(data)
    cache.set(key, state, _PROGRESS_TTL)
    return state

def _process_excel_background(upload_id: str, file_path: str, uploader_id: int, file_name: str):
    """
    معالجة الإكسل في الخلفية + تحديث نسبة التقدم في الكاش.
    """
    try:
        _set_progress(upload_id, status='running', processed=0, total=0, percent=0)

        # نقرأ الإكسل بنفس إعداداتك (خليها XLSX)
        df = pd.read_excel(file_path, dtype=str, na_filter=False, keep_default_na=False, engine='openpyxl')
        df = df.fillna('')

        total = len(df.index)
        _set_progress(upload_id, total=total)

        # الشهر الحالي (أول يوم في الشهر)
        current_month = datetime.now().date().replace(day=1)

        # امسح مفردات الشهر الحالي فقط (زي ما كنت عامل)
        SalaryStatement.objects.filter(month=current_month).delete()

        processed = 0

        # عالج صفوف الملف
        for _, row in df.iterrows():
            # أساسيّات
            employee_id = str(row['رقم تعريفى'])
            name = row['الاسم']

            # حقول ثابتة تُخزّن على المستخدم وتُحدّث كل رفع
            branch = str(row.get('اسم الفرع') or row.get('الفرع') or '').strip()
            bank_raw = row.get('رقم الحساب البنكي') or row.get('رقم الحساب') or ''
            bank = normalize_bank_account(bank_raw)

            base_raw = (
                row.get('المرتب الاساسي') or
                row.get('الراتب الأساسي') or
                row.get('الراتب الاساسي') or
                row.get('الراتب الاساسى') or
                row.get('basic_salary') or
                row.get('base_salary') or
                row.get('base salary')
            )
            base_salary_dec = to_decimal(base_raw)

            # باقي أعمدة المفردات (على مستوى الشهر)
            base_salary = row['المرتب الاساسي']
            changed_salary = row['المرتب المتغير']
            special_bonus = row['علاوة استثنائية']
            extra = row['الاضافى']
            rest_allowance = row['بدل الراحة']
            performance_evaluation = row['تقييم أداء']
            special_incentive = row['حافز استثنائى']
            meal_allowance = row['بدل وجبة']
            transport_allowance = row['بدل انتقال']
            total_entitlements = row['اجمالي الاستحقاقات']

            loan = row['السلف']
            insurance = row['تأمينات']
            absence = row['الغياب']
            penalties = row['الجزاءات']
            quality_deduction_cash = row['خصم الجودة نقدى']
            quality_deduction_days = row['خصم الجودة أيام']
            installments = row['الأقساط']
            monthly_receipts = row['الايصالات الشهرية']
            total_deductions = row['اجمالي الاستقطاعات']
            net_salary = row['صافي المرتبات']
            notes = row.get('ملاحظات', '')

            # احضر/أنشئ المستخدم
            user, created = CustomUser.objects.get_or_create(
                employee_id=employee_id,
                defaults={
                    'username': employee_id,
                    'first_name': name.split()[0] if name else '',
                    'last_name': ' '.join(name.split()[1:]) if name else '',
                    'role': 'user',
                }
            )

            # حدّث الحقول الثابتة لو موجودة
            changed_user = False
            if branch and user.branch_name != branch:
                user.branch_name = branch
                changed_user = True
            if bank and user.bank_account_number != bank:
                user.bank_account_number = bank
                changed_user = True
            if (base_salary_dec is not None) and (user.base_salary != base_salary_dec):
                user.base_salary = base_salary_dec
                changed_user = True
            if changed_user:
                user.save()

            if created:
                user.set_password('0000')
                user.is_defult_password = True
                user.save()

            # أنشئ مفردات الشهر
            SalaryStatement.objects.create(
                user=user,
                month=current_month,
                base_salary=base_salary,
                changed_salary=changed_salary,
                special_bonus=special_bonus,
                extra=extra,
                rest_allowance=rest_allowance,
                performance_evaluation=performance_evaluation,
                special_incentive=special_incentive,
                meal_allowance=meal_allowance,
                transport_allowance=transport_allowance,
                total_entitlements=total_entitlements,
                loan=loan,
                insurance=insurance,
                absence=absence,
                penalties=penalties,
                quality_deduction_cash=quality_deduction_cash,
                quality_deduction_days=quality_deduction_days,
                installments=installments,
                monthly_receipts=monthly_receipts,
                total_deductions=total_deductions,
                net_salary=net_salary,
                notes=notes,
            )

            processed += 1
            if total and (processed % 10 == 0 or processed == total):
                _set_progress(upload_id, processed=processed, percent=int(processed * 100 / total))

        # سجل رفع واحد (بدل ما يبقى لكل صف)
        ExcelUploadLog.objects.create(
            uploader_id=uploader_id,
            file_name=file_name,
            sheet_name='Sheet1',
            month=current_month,
        )

        _set_progress(upload_id, processed=processed, percent=100, status='done')

    except KeyError as e:
        _set_progress(upload_id, status='error', error=f'عمود مفقود في الملف: {e}')
    except Exception as e:
        _set_progress(upload_id, status='error', error=str(e))
    finally:
        try:
            os.remove(file_path)
        except Exception:
            pass

@login_required
@user_passes_test(lambda u: not u.is_defult_password, login_url=reverse_lazy('reset-password'))
def salary_upload_start(request):
    """يبدأ رفع الملف ويطلق المعالجة في خلفية (Thread) مع Progress في الكاش."""
    if request.user.role not in ['admin', 'hr']:
        return HttpResponseForbidden("🚫 You don't have permission to access this page.")
    if request.method != 'POST':
        return HttpResponseBadRequest('Invalid method')

    f = request.FILES.get('file')
    if not f:
        return JsonResponse({'ok': False, 'msg': 'لم يتم اختيار ملف'})

    fd, tmp_path = tempfile.mkstemp(prefix='salary_', suffix='.xlsx')
    with os.fdopen(fd, 'wb') as out:
        for chunk in f.chunks():
            out.write(chunk)

    upload_id = str(uuid.uuid4())
    _set_progress(upload_id, status='queued', percent=0, processed=0, total=0)

    threading.Thread(
        target=_process_excel_background,
        args=(upload_id, tmp_path, request.user.id, f.name),
        daemon=True
    ).start()

    return JsonResponse({'ok': True, 'upload_id': upload_id})

@login_required
@user_passes_test(lambda u: not u.is_defult_password, login_url=reverse_lazy('reset-password'))
def salary_upload_progress(request, upload_id: str):
    """Polling لحالة ونسبة التقدّم."""
    state = cache.get(_progress_key(upload_id)) or {}
    if not state:
        return JsonResponse({'ok': False, 'status': 'unknown'})
    state['ok'] = True
    return JsonResponse(state)
# =============== نهاية الرفع بــ Progress ===============

@login_required
@user_passes_test(lambda u: not u.is_defult_password, login_url=reverse_lazy('reset-password'))
def upload_salary_excel(request):
    """
    صفحة الرفع فقط (تعرض الفورم والسجل).
    الرفع الفعلي يتم عبر endpoint: salary-upload-start + polling progress.
    """
    if request.user.role not in ['admin', 'hr']:
        return HttpResponseForbidden("🚫 You don't have permission to access this page.")

    form = UploadFileForm()
    logs = ExcelUploadLog.objects.order_by('-upload_time')[:1]
    return render(request, 'salaries/upload_excel.html', {'form': form, 'logs': logs})

@login_required
@user_passes_test(lambda user: user.role in ['admin', 'hr'])
def delete_all_salaries(request):
    SalaryStatement.objects.all().delete()
    messages.success(request, "✅ تم حذف جميع بيانات المرتبات بنجاح.")
    return redirect('upload_excel')

@login_required
@user_passes_test(lambda u: not u.is_defult_password, login_url=reverse_lazy('reset-password'))
def salary_list(request):

    if request.user.role in ['admin', 'hr']:
        salary_statements = SalaryStatement.objects.select_related('user').filter(user__is_active=True)
    else:
        salary_statements = SalaryStatement.objects.filter(user=request.user, user__is_active=True)

    search_query = request.GET.get('search', '')
    if search_query:
        if request.user.role in ['admin', 'hr']:
            salary_statements = salary_statements.filter(
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(user__employee_id__icontains=search_query)
            )
        else:
            salary_statements = salary_statements.filter(
                Q(user__employee_id__icontains=search_query)
            )

    salary_statements = salary_statements.order_by('-month')
    paginator = Paginator(salary_statements, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'salaries/salary_list.html', {'page_obj': page_obj})

@login_required
@user_passes_test(lambda u: not u.is_defult_password, login_url=reverse_lazy('reset-password'))
def salary_slip_detail(request, pk):
    slip = get_object_or_404(SalaryStatement, id=pk)

    if not request.user.role in ['admin', 'hr'] and slip.user != request.user:
        raise PermissionDenied

    if request.method == 'POST' and request.user.role in ['admin', 'hr']:
        notes = request.POST.get('notes', '')
        slip.notes = notes
        slip._current_user = request.user
        slip.save(update_fields=['notes'])
        messages.success(request, 'تم تحديث الملاحظات بنجاح')
        return redirect('salary_detail', pk=slip.id)

    return render(request, 'salaries/salary_slip_detail.html', {'slip': slip})

from django.contrib.auth import get_user_model
from django.contrib import messages
User = get_user_model()

@login_required
@user_passes_test(lambda u: u.role in ['admin', 'hr'])
def reset_user_password(request, pk):
    target_user = get_object_or_404(User, id=pk)

    if target_user.role != 'user':
        messages.error(request, 'لا يمكن إعادة تعيين كلمة المرور لهذا المستخدم.')
        return redirect(request.META.get('HTTP_REFERER', '/'))

    target_user.set_password('0000')
    target_user.is_defult_password = True
    target_user.save()

    messages.success(request, f"تمت إعادة تعيين كلمة المرور للمستخدم {target_user.username} إلى 0000.")
    return redirect(request.META.get('HTTP_REFERER', '/'))
