from django.urls import path
from .views import AccUsersAPIView, TbItemMasterAPIView

urlpatterns = [
    path('api/acc_users/', AccUsersAPIView.as_view(), name='acc_users_api'),
    path('api/items/', TbItemMasterAPIView.as_view(), name='items_api'),
]