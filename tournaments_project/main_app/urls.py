from django.urls import path
# from . import views
from .views import login_view, main_view, registration_view

urlpatterns = [
    path('', main_view.index, name='index'),
    path('add-user/', registration_view.AddUser.as_view(), name='add_user'),
    path('delete-user/', main_view.delete_user, name='delete_user'),
    path('login-user/', login_view.LoginUser.as_view(), name='login_user'),
]