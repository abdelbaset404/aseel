from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.db.models import Sum
from .models import Collection, Loan, Borrower

def _recompute_loan(loan: Loan):
    agg = loan.collections.aggregate(paid=Sum("amount"))
    total_paid = agg["paid"] or 0
    loan.total_paid = total_paid
    loan.total_remaining = max(loan.amount - total_paid, 0)
    # لو خلصت القيمة المتبقية = 0، اتحول تلقائياً لمكتمل (إلا لو ديون معدومة يدويًا)
    if loan.status != Loan.BAD_DEBT:
        loan.status = Loan.CLOSED if loan.total_remaining == 0 else Loan.ACTIVE
    loan.save(update_fields=["total_paid", "total_remaining", "status"])

def _recompute_borrower(b: Borrower):
    loans = b.loans.all()
    b.loans_count = loans.count()
    b.loans_total = loans.aggregate(s=Sum("amount"))["s"] or 0
    b.loans_total_paid = loans.aggregate(s=Sum("total_paid"))["s"] or 0
    b.loans_total_remaining = loans.aggregate(s=Sum("total_remaining"))["s"] or 0
    b.save(update_fields=["loans_count","loans_total","loans_total_paid","loans_total_remaining"])

@receiver(post_save, sender=Collection)
def after_collection_saved(sender, instance: Collection, created, **kwargs):
    loan = instance.loan
    loan.last_collection_at = instance.collected_at
    loan.save(update_fields=["last_collection_at"])
    _recompute_loan(loan)
    _recompute_borrower(loan.borrower)

@receiver(post_delete, sender=Collection)
def after_collection_deleted(sender, instance: Collection, **kwargs):
    loan = instance.loan
    _recompute_loan(loan)
    _recompute_borrower(loan.borrower)

@receiver(pre_save, sender=Loan)
def before_loan_saved(sender, instance: Loan, **kwargs):
    # عند إنشاء قرض جديد، اجعل المتبقي = المبلغ
    if instance._state.adding:
        instance.total_remaining = instance.amount
