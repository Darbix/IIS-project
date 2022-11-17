from django.urls import path
from .views import login_admin_view, main_admin_view

urlpatterns = [
    path('login/', login_admin_view.LoginAdmin.as_view(), name='login_admin'),
    path('', main_admin_view.MainAdmin.as_view(), name='admin'),
    path('delete-user/', main_admin_view.MainAdmin.as_view(), name='delete_user')
]