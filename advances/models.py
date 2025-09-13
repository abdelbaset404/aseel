from django.conf import settings
from django.db import models
from django.utils import timezone

# إضافات مطلوبة للتحقق الحسابي والرسائل
from decimal import Decimal, InvalidOperation
from django.core.exceptions import ValidationError


class AdvanceType(models.TextChoices):
    FIRST = 'FIRST', 'السلفة الأولى'
    SECOND = 'SECOND', 'السلفة الثانية'


class AdvanceStatus(models.TextChoices):
    UNDER_REVIEW = 'UNDER_REVIEW', 'تحت المراجعة'
    APPROVED = 'APPROVED', 'تم القبول'
    REJECTED = 'REJECTED', 'تم الرفض'


class AdvancePeriod(models.Model):
    """فترة السماح لكل نوع سلفة"""
    advance_type = models.CharField(max_length=10, choices=AdvanceType.choices)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.get_advance_type_display()} | {self.start_date} → {self.end_date}"

    def is_open_now(self):
        today = timezone.localdate()
        return self.is_active and self.start_date <= today <= self.end_date


class AdvanceRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    advance_type = models.CharField(max_length=10, choices=AdvanceType.choices)
    period = models.ForeignKey(AdvancePeriod, on_delete=models.PROTECT, related_name='requests')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)

    # الحالة النهائية (لا تتحول إلا عند التأكيد النهائي)
    status = models.CharField(max_length=20, choices=AdvanceStatus.choices,
                              default=AdvanceStatus.UNDER_REVIEW)

    # قرار إداري مبدئي (لا يغيّر status إلا بعد التأكيد النهائي)
    admin_decision = models.CharField(max_length=20, choices=AdvanceStatus.choices,
                                      null=True, blank=True)

    # منع تعديل الموظف بمجرد وجود قرار إداري مبدئي
    user_locked = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # قفل نهائي (بعد التأكيد) — يمنع التعديل حتى للإدمن حسب منطقك إن أردت
    locked = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['user', 'advance_type', 'period'],
                                    name='unique_user_type_period'),
        ]

    @property
    def is_complete(self):
        # اعتبر الطلب "مكتمل" لو خرج من تحت المراجعة نهائيًا (أو تم قفله)
        return self.status != AdvanceStatus.UNDER_REVIEW or self.locked

    # =========
    # ✅ القيود المطلوبة + عرض الحدود للموظف
    # =========

    @property
    def allowed_min(self) -> Decimal | None:
        """
        أقل مبلغ مسموح: 100 إذا كان عنده راتب أساسي > 0، وإلا None (غير مسموح بالتقديم).
        """
        base = getattr(self.user, 'base_salary', None) or Decimal('0')
        return Decimal('100') if base > 0 else None

    @property
    def allowed_max(self) -> Decimal | None:
        """
        أعلى مبلغ مسموح: ربع الراتب الأساسي إذا كان >0، وإلا None (غير مسموح بالتقديم).
        """
        base = getattr(self.user, 'base_salary', None) or Decimal('0')
        if base <= 0:
            return None
        try:
            base = Decimal(base)
        except InvalidOperation:
            return None
        return (base / Decimal('4')).quantize(Decimal('0.01'))

    def allowed_range_text(self) -> str:
        """
        نص جاهز للعرض للمستخدم يوضح الحدود.
        """
        amin = self.allowed_min
        amax = self.allowed_max
        if amin is None or amax is None or amax <= 0:
            return "غير مسموح بطلب سلفة: لا يوجد راتب أساسي مُسجَّل أو قيمته صفر."
        return f"مسموح لك بطلب سلفة من {amin:.2f} إلى {amax:.2f}."

    def clean(self):
        # لو لسه الـ user متعيّنش (قبل form.instance.user)، سيب التحقق لغاية save()
        if not self.user_id:
            return
        """
        الشروط:
        - لازم يكون عنده راتب أساسي > 0 (وإلا الطلب مرفوض).
        - أقل مبلغ 100.
        - أقصى مبلغ = ربع الراتب الأساسي.
        """
        # تحضير القيم
        base = getattr(self.user, 'base_salary', None) or Decimal('0')
        try:
            base = Decimal(base)
        except InvalidOperation:
            base = Decimal('0')

        try:
            amt = Decimal(self.amount or 0)
        except InvalidOperation:
            raise ValidationError("قيمة السلفة غير صالحة.")

        # شرط وجود راتب أساسي > 0
        if base <= 0:
            raise ValidationError("غير مسموح بطلب سلفة بدون راتب أساسي مثبت أو إذا كان 0.")

        # الحد الأدنى 100
        if amt < Decimal('100'):
            raise ValidationError("السلفة لا تقل عن 100.")

        # الحد الأقصى ربع الراتب
        limit = (base / Decimal('4')).quantize(Decimal('0.01'))
        if amt > limit:
            raise ValidationError(f"السلفة لا تزيد عن ربع الراتب الأساسي ({limit:.2f}).")

    def save(self, *args, **kwargs):
        # تأكيد تنفيذ القيود في كل المسارات (أدمن/فورم/API)
        self.full_clean()
        return super().save(*args, **kwargs)
