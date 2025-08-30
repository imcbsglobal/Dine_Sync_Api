from django.urls import path
from .views import AccUsersAPIView, TbItemMasterAPIView,DineBillAPIView

urlpatterns = [
    path('api/acc_users/', AccUsersAPIView.as_view(), name='acc_users_api'),
    path('api/items/', TbItemMasterAPIView.as_view(), name='items_api'),
    path('api/bills/', DineBillAPIView.as_view(), name='bills_api'),  # NEW: Bills endpoint
]