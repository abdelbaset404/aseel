from django.conf import settings
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone

loan_number = models.CharField(max_length=30, unique=True, editable=False)
NATIONAL_ID_VALIDATOR = RegexValidator(
    regex=r"^\d{14}$", message="الرقم القومي يجب أن يكون 14 رقمًا."
)
PHONE_VALIDATOR = RegexValidator(
    regex=r"^\d{11}$", message="رقم الهاتف يجب أن يكون 11 رقمًا."
)

class Borrower(models.Model):
    EMPLOYEE = "employee"
    EXTERNAL = "external"
    BORROWER_TYPE_CHOICES = [
        (EMPLOYEE, "ضمن الموظفين"),
        (EXTERNAL, "خارج الموظفين"),
    ]

    national_id = models.CharField(
        max_length=14, unique=True, validators=[NATIONAL_ID_VALIDATOR]
    )
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=11, validators=[PHONE_VALIDATOR], blank=True)
    address = models.CharField(max_length=250, blank=True)
    borrower_type = models.CharField(
        max_length=10, choices=BORROWER_TYPE_CHOICES, default=EMPLOYEE
    )

    # مجاميع للتجميعات السريعة (denormalized)
    loans_count = models.PositiveIntegerField(default=0)
    loans_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    loans_total_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    loans_total_remaining = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.full_name} ({self.national_id})"


class Loan(models.Model):
    # آخر مبلغ تحصيل مخزَّن للتقارير والتصدير
    last_collect_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    ACTIVE = "active"
    CLOSED = "closed"
    BAD_DEBT = "bad_debt"
    STATUS_CHOICES = [
        (ACTIVE, "مستمر"),
        (CLOSED, "مكتمل"),
        (BAD_DEBT, "ديون معدومة"),
    ]

    MONTHLY = "monthly"
    ONEOFF = "oneoff"
    REPAYMENT_CHOICES = [
        (MONTHLY, "أقساط شهرية"),
        (ONEOFF, "دفعة واحدة"),
    ]

    loan_number = models.CharField(max_length=30, unique=True, editable=False)  # editable=False يخفيه من الفورم
    borrower = models.ForeignKey(Borrower, on_delete=models.PROTECT, related_name="loans")

    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=ACTIVE)
    repayment_type = models.CharField(max_length=10, choices=REPAYMENT_CHOICES)

    monthly_installment = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )  # مطلوب إذا كانت أقساط شهرية
    received_at = models.DateTimeField(default=timezone.now)  # الوقت/التاريخ الحالي
    maturity_date = models.DateField(null=True, blank=True)   # مطلوب لو دفعة واحدة

    total_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_remaining = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    last_collection_at = models.DateTimeField(null=True, blank=True)

    def clean(self):
        # قواعد التحقق حسب متطلباتك (نوع السداد والقيم)
        from django.core.exceptions import ValidationError
        if self.repayment_type == Loan.MONTHLY and (self.monthly_installment is None):
            raise ValidationError("قيمة القسط الشهري مطلوبة عند اختيار (أقساط شهرية).")
        if self.repayment_type == Loan.ONEOFF and (self.maturity_date is None):
            raise ValidationError("تاريخ الاستحقاق مطلوب عند اختيار (دفعة واحدة).")

    def __str__(self):
        return f"Loan {self.loan_number} - {self.borrower.full_name}"


class Collection(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name="collections")
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    collected_at = models.DateTimeField(default=timezone.now)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"تحصيل {self.amount} على {self.loan.loan_number}"


class ActivityLog(models.Model):
    # سجل قراءة فقط لاحقًا في الواجهة
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    action = models.CharField(max_length=50)  # ADD_LOAN / COLLECT / UPDATE_STATUS / EXPORT ...
    target_model = models.CharField(max_length=50, blank=True)
    target_id = models.CharField(max_length=50, blank=True)
    payload = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
