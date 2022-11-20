from django.urls import path
from .views import login_view, main_view, logout_view, query_view, tournaments_view

urlpatterns = [
    path('', main_view.MainAdmin.as_view(), name='dashboard'),
    path('login/', login_view.LoginAdmin.as_view(), name='login'),
    path('logout/', logout_view.LogoutAdmin.as_view(), name='logout'),
    path('query/', query_view.QueryTable.as_view(), name='query'),
    path('tournaments/', tournaments_view.Tournaments.as_view(), name='tournaments')
]