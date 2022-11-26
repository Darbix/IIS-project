from django.urls import path
from .views import login_view, main_view, logout_view, query_view, tournaments_view, users_view, admins_view

urlpatterns = [
    path('', main_view.MainAdmin.as_view(), name='dashboard'),
    path('login/', login_view.LoginAdmin.as_view(), name='login'),
    path('logout/', logout_view.LogoutAdmin.as_view(), name='logout'),
    path('query/', query_view.QueryTable.as_view(), name='query'),
    path('tournaments/', tournaments_view.Tournaments.as_view(), name='tournaments'),
    path('tournaments/<int:event_id>/', tournaments_view.Tournaments.as_view(), name='tournaments'),
    path('users/', users_view.Users.as_view(), name='users'),
    path('users/<int:user_id>/', users_view.Users.as_view(), name='users'),
    path('admins/', admins_view.Admins.as_view(), name='admins'),
    path('admins/<int:admin_id>/', admins_view.Admins.as_view(), name='admins'),
]