from django.urls import path
# from . import views
from .views import login_view, main_view, registration_view, profile_view, logout_view, events_view, event_view, teams_view

urlpatterns = [
    path('', main_view.index, name='index'),
    path('register-user/', registration_view.AddUser.as_view(), name='register_user'),
    path('login-user/', login_view.LoginUser.as_view(), name='login_user'),
    path('logout-user/', logout_view.LogoutUser.as_view(), name='logout_user'),
    path('user-profile/', profile_view.Profile.as_view(), name='user_profile'),
    path('upload-profile-img/', profile_view.ProfileImageUpload.as_view(), name='upload_user_image'),
    
    path('user-teams/', teams_view.Teams.as_view(), name='user_teams'),
    path('user-teams/add-teammate/', teams_view.AddTeammate.as_view(), name='add_teammate'),
    path('user-teams/remove-teammate/', teams_view.RemoveTeammate.as_view(), name='remove_teammate'),
    path('user-teams/create-team/', teams_view.CreateTeam.as_view(), name='create_team'),
    path('user-teams/delete-team/', teams_view.DeleteTeam.as_view(), name='delete_team'),
    path('user-teams/unjoin-event/', teams_view.UnjoinEvent.as_view(), name='unjoin_event'),

    path('events/', events_view.Events.as_view(), name='events'),
    path('events/<int:event_id>/', event_view.Event.as_view(), name='event'),
    path('events/<int:event_id>/join/', event_view.Event.as_view(), name='join_tournament'),
    path('events/<int:event_id>/unjoin/', event_view.EventUnjoin.as_view(), name='unjoin_tournament'),
]