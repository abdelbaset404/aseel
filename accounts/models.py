from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('hr', 'HR'),
        ('user', 'User'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    employee_id = models.CharField(max_length=20, unique=True)
    branch_name = models.CharField(max_length=255, blank=True, null=True)
    bank_account_number = models.CharField(max_length=64, blank=True, null=True)
    base_salary = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    is_defult_password = models.BooleanField(default=True)
    USERNAME_FIELD = 'employee_id'
    REQUIRED_FIELDS = ['username', 'role']
    def __str__(self):
        return f"{self.username} - {self.role}"
