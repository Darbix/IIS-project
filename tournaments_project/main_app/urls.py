from django.urls import path
# from . import views
from .views import login_view, main_view, registration_view, profile_view, logout_view

urlpatterns = [
    path('', main_view.index, name='index'),
    path('register-user/', registration_view.AddUser.as_view(), name='register_user'),
    path('login-user/', login_view.LoginUser.as_view(), name='login_user'),
    path('logout-user/', logout_view.LogoutUser.as_view(), name='logout_user'),
    path('user-profile/', profile_view.Profile.as_view(), name='user_profile'),
    path('upload-profile-img/', profile_view.ProfileImageUpload.as_view(), name='upload_user_image'),
]