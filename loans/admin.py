from django.contrib import admin
from .models import Borrower, Loan, Collection, ActivityLog

@admin.register(Borrower)
class BorrowerAdmin(admin.ModelAdmin):
    list_display = ("full_name","national_id","borrower_type","loans_count","loans_total_remaining")
    search_fields = ("full_name","national_id","phone")
    list_filter = ("borrower_type",)

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ("loan_number","borrower","amount","status","repayment_type","monthly_installment","total_paid","total_remaining","received_at","maturity_date","last_collection_at")
    list_filter = ("status","repayment_type")
    search_fields = ("loan_number","borrower__national_id","borrower__full_name")

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ("loan","amount","collected_at")
    search_fields = ("loan__loan_number","loan__borrower__national_id")

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("action","actor","target_model","target_id","created_at")
    search_fields = ("action","target_model","target_id")
    readonly_fields = ("created_at",)
