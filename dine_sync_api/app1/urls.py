from django.urls import path
from .views import AccUsersAPIView, TbItemMasterAPIView, DineBillAPIView, DineKotSalesDetailAPIView, CancelledBillsAPIView,DineBillMonthAPIView

urlpatterns = [
    path('api/acc_users/', AccUsersAPIView.as_view(), name='acc_users_api'),
    path('api/items/', TbItemMasterAPIView.as_view(), name='items_api'),
    path('api/bills/', DineBillAPIView.as_view(), name='bills_api'),
    path('api/bills_month/', DineBillMonthAPIView.as_view(), name='bills_month_api'),  # NEW: Bills Month endpoint
    path('api/kot_sales/', DineKotSalesDetailAPIView.as_view(), name='kot_sales_api'),
    path('api/cancelled_bills/', CancelledBillsAPIView.as_view(), name='cancelled_bills_api'),  # NEW: Cancelled Bills endpoint
]