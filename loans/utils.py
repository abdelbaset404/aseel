from django.utils import timezone
from .models import Loan   # ✅ الاستيراد الصحيح

def generate_loan_number():
    # مثال: LOAN-20250908-0001
    prefix = timezone.now().strftime("LOAN-%Y%m%d-")
    last = Loan.objects.filter(loan_number__startswith=prefix).count() + 1
    return f"{prefix}{last:04d}"
