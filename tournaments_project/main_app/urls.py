from django.urls import path
# from . import views
from .views import login_view, main_view, registration_view

urlpatterns = [
    path('', main_view.index, name='index'),
    path('add-user/', registration_view.AddUser.as_view(), name='add_user'),
    path('delete-user/', main_view.delete_user, name='delete_user'),
    path('login-user/', login_view.LoginUser.as_view(), name='login_user'),

    #TODO temp url paths
    path('register-user/', main_view.register_todo, name='register_user'),
    path('user-profile/', main_view.profile_todo, name='user_profile'),

]