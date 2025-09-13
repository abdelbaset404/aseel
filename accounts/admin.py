from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from .models import CustomUser

# فورم لتصغير عرض خانات الفرع/الحساب/الراتب في صفحات الإضافة/التعديل وكمان list_editable
class CustomUserAdminForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = '__all__'
        widgets = {
            'branch_name': forms.TextInput(attrs={'style': 'width:80px'}),
            'bank_account_number': forms.TextInput(attrs={'style': 'width:80px'}),
            'base_salary': forms.NumberInput(attrs={'style': 'width:80px'}),
        }

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    form = CustomUserAdminForm

    # رجّعت role + أضفت is_defult_password بالظبط زي admin1.py
    list_display = (
        'employee_id', 'username', 'role',
        'first_name', 'last_name',
        'branch_name', 'bank_account_number', 'base_salary',
        'is_defult_password',           # 👈 نفس الاسم الموجود عندك في الموديل/admin1
        'is_active', 'is_staff', 'is_superuser'
    )
    list_editable = ('branch_name', 'bank_account_number', 'base_salary')

    search_fields = (
        'employee_id', 'username', 'email', 'first_name', 'last_name',
        'branch_name', 'bank_account_number'
    )
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser', 'branch_name', 'is_defult_password')
    ordering = ('employee_id', 'username', 'role')

    # نضبط كمان عرض الحقول في list_editable
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if formfield and db_field.name in ('branch_name', 'bank_account_number', 'base_salary'):
            style = formfield.widget.attrs.get('style', '')
            if db_field.name == 'branch_name':
                style += 'width:80px;'
            elif db_field.name == 'bank_account_number':
                style += 'width:80px;'
            elif db_field.name == 'base_salary':
                style += 'width:80px;'
            formfield.widget.attrs['style'] = style
        return formfield

    fieldsets = (
        # أضفت is_defult_password في أول جروب زي ما شوفتك مستخدمه في admin1
        (None, {'fields': ('username', 'password', 'is_defult_password')}),
        ('Personal info', {
            'fields': (
                'first_name', 'last_name', 'email',
                'employee_id', 'branch_name', 'bank_account_number', 'base_salary',
            )
        }),
        ('Permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'employee_id', 'username', 'email', 'password1', 'password2',
                'role', 'is_active', 'is_staff', 'is_superuser',
                'branch_name', 'bank_account_number', 'base_salary',
            ),
        }),
    )

    filter_horizontal = ('groups', 'user_permissions')
