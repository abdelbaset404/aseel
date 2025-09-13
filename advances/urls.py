# advances/urls.py
from django.urls import path, include
from . import views
#----------------------------------------------------------
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdvanceRequestViewSet, AdvanceEligibilityView

router = DefaultRouter()
# لازم نحط basename لأن مفيش queryset ثابت
router.register(r'requests', AdvanceRequestViewSet, basename='advance-requests')
urlpatterns = [
    # واجهة الموظف
    path('my-advances/', views.user_advances_portal, name='user-advances'),
    path('submit/', views.submit_advance, name='submit-advance'),
    path('my/edit/<int:pk>/', views.user_edit_advance, name='adv-user-edit'),
    path('user/delete/<int:pk>/', views.user_delete_advance, name='adv-user-delete'),

    # إدارة مواعيد السُلف
    path('admin/periods/', views.periods_manage, name='adv-periods'),

    # إدارة الطلبات للأدمن
    path('admin/requests/', views.requests_list, name='adv-requests'),
    path('admin/requests/<int:pk>/edit/', views.admin_edit_request, name='adv-admin-edit'),

    # قبول/رفض فردي (الأسماء اللي بتستخدمها في التمبلت)
    path('admin/requests/<int:pk>/approve/', views.approve_one, name='adv-approve-one'),
    path('admin/requests/<int:pk>/reject/',  views.reject_one,  name='adv-reject-one'),

    # بَلك أكشن
    path('admin/requests/bulk/confirm-no-review/', views.confirm_when_no_under_review, name='adv-confirm-no-review'),
    path('admin/requests/bulk/approve-rest/',     views.approve_rest,               name='adv-approve-rest'),
    path('admin/requests/bulk/reject-rest/',      views.reject_rest,                name='adv-reject-rest'),

    # تصدير Excel
    path('admin/requests/export/', views.export_requests_xlsx, name='adv-export'),

    # عمليات مساعدة
    path('admin/reset/',         views.full_month_reset,          name='adv-month-reset'),
    path('admin/delete-first/',  views.delete_first_advance_requests, name='adv-delete-first'),
    path('admin/sync-push/',     views.sync_push,                 name='adv-sync-push'),
    path('api/advances/', include(router.urls)),
    #--------------------------
    path('api/advances/', include(router.urls)),
    #-------------------------------
    path('api/advances/eligibility/', AdvanceEligibilityView.as_view(), name='advance-eligibility'),
]
