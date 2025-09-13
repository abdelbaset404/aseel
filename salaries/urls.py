from django.urls import path, include
from .views import *

urlpatterns = [
    path('', salary_list, name='salary_list'),
    path('salary-details/<int:pk>/', salary_slip_detail, name='salary_detail'),

    # صفحة الرفع (تعرض الفورم والسجل فقط)
    path('upload/', upload_salary_excel, name='upload_excel'),

    # Endpoints الرفع الحقيقي مع Progress
    path('upload/start/', salary_upload_start, name='salary-upload-start'),
    path('upload/progress/<str:upload_id>/', salary_upload_progress, name='salary-upload-progress'),

    path('my-slip/', MySalaryStatements.as_view(), name='my-slip'),
    path('reset-password/<int:pk>/', reset_user_password, name='reset-user-password'),
    path('delete-all-salaries/', delete_all_salaries, name='delete-all-salaries'),

    path('advances/', include('advances.urls')),
]
