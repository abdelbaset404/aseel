from django.urls import path
from . import views

app_name = "loans"

urlpatterns = [
    path('', views.loan_list, name='list'),
    path("", views.loan_list, name="loan_list"),
    path("add/", views.loan_add, name="loan_add"),
    path("<str:loan_number>/collect/", views.collect_payment, name="collect_payment"),
    path("export/xlsx/", views.export_loans_xlsx, name="export_loans_xlsx"),
    path("inquiry/", views.inquiry, name="inquiry"),
    path("inquiry/export/xlsx/", views.inquiry_export_xlsx, name="inquiry_export_xlsx"),
    path("logs/", views.logs_readonly, name="logs"),
    path("prefill-by-nid/", views.prefill_by_national_id, name="prefill_by_nid"),
]
