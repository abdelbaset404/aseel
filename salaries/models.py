from django.db import models
from accounts.models import CustomUser

class SalaryStatement(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    month = models.DateField()

    base_salary = models.DecimalField(max_digits=10, decimal_places=2)
    changed_salary = models.DecimalField(max_digits=10, decimal_places=2)
    special_bonus = models.DecimalField(max_digits=10, decimal_places=2)
    extra = models.DecimalField(max_digits=10, decimal_places=2)
    rest_allowance = models.DecimalField(max_digits=10, decimal_places=2)
    performance_evaluation = models.CharField(max_length=255, blank=True, null=True)  
    special_incentive = models.DecimalField(max_digits=10, decimal_places=2)
    meal_allowance = models.DecimalField(max_digits=10, decimal_places=2)
    transport_allowance = models.DecimalField(max_digits=10, decimal_places=2)
    total_entitlements = models.DecimalField(max_digits=10, decimal_places=2)

    loan = models.DecimalField(max_digits=10, decimal_places=2)
    insurance = models.DecimalField(max_digits=10, decimal_places=2)
    absence = models.DecimalField(max_digits=10, decimal_places=2)
    penalties = models.DecimalField(max_digits=10, decimal_places=2)
    quality_deduction_cash = models.DecimalField(max_digits=10, decimal_places=2)
    quality_deduction_days = models.DecimalField(max_digits=10, decimal_places=2)
    installments = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_receipts = models.DecimalField(max_digits=10, decimal_places=2)
    total_deductions = models.DecimalField(max_digits=10, decimal_places=2)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)

    notes = models.TextField(blank=True, null=True, default="")
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_salaries')
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if 'notes' in kwargs.get('update_fields', []) or kwargs.get('force_insert', False):
            if hasattr(self, '_current_user'):
                self.updated_by = self._current_user
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.month.strftime('%B %Y')}"


from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ExcelUploadLog(models.Model):
    uploader = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    upload_time = models.DateTimeField(auto_now_add=True)
    file_name = models.CharField(max_length=255)
    sheet_name = models.CharField(max_length=255, blank=True, null=True)
    month = models.DateField(null=True, blank=True) 

    def __str__(self):
        return f"{self.file_name} uploaded by {self.uploader} at {self.upload_time.strftime('%Y-%m-%d %H:%M')}"
