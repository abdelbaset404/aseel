from django.contrib import admin
from .models import SalaryStatement

@admin.register(SalaryStatement)
class SalaryStatementAdmin(admin.ModelAdmin):
    list_display = (
        'get_full_name', 'month', 'base_salary', 'changed_salary',
        'total_entitlements', 'total_deductions', 'net_salary',
        'updated_by', 'updated_at'
    )
    search_fields = ('user__username', 'user__employee_id', 'user__first_name', 'user__last_name')
    list_filter = ('user',)  
    ordering = ('-month',)

    readonly_fields = (
        'updated_by', 'updated_at', 
        'net_salary', 'total_entitlements', 'total_deductions'
    )

    fieldsets = (
        ('Employee Info', {
            'fields': ('user', 'month'),
            'description': 'You can search by username, employee ID, or full name.'
        }),
        ('Salary & Earnings', {
            'fields': (
                'base_salary', 'changed_salary', 'special_bonus', 'extra',
                'rest_allowance', 'special_incentive', 'meal_allowance', 'transport_allowance',
                'performance_evaluation', 'total_entitlements'
            )
        }),
        ('Deductions', {
            'fields': (
                'loan', 'insurance', 'absence', 'penalties',
                'quality_deduction_cash', 'quality_deduction_days',
                'installments', 'monthly_receipts', 'total_deductions'
            )
        }),
        ('Net Salary', {
            'fields': ('net_salary',)
        }),
        ('Notes & Update Info', {
            'fields': ('notes', 'updated_by', 'updated_at')
        }),
    )

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name} ({obj.user.employee_id})"
    get_full_name.short_description = 'Employee'

    def save_model(self, request, obj, form, change):
        obj._current_user = request.user
        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        return True
