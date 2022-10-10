from django.urls import path
# from . import views
from .views import login_view, main_view

urlpatterns = [
    path('', main_view.index, name='index'),
    path('add-user/', main_view.add_user, name='add_user'),
    path('add-user/add-user-post/', main_view.add_user_post, name='add_user_post'),
    path('delete-user/', main_view.delete_user, name='delete_user'),
    path('delete-user/delete-user-post/', main_view.delete_user_post, name='delete_user_post'),
    
    path('login-user/', login_view.login_user, name='login_user'),

]