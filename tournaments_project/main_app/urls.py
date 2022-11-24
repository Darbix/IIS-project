from django.urls import path
# from . import views
from .views import login_view, main_view, registration_view, profile_view, logout_view, events_view, event_view, teams_view, results_view, result_view

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
    path('user-teams/change-name/', teams_view.ChangeName.as_view(), name='change_name'),
    path('user-teams/upload-team-img/', teams_view.TeamImageUpload.as_view(), name='team_image'),

    path('events/', events_view.Events.as_view(), name='events'),
    path('events/create/', events_view.EventCreate.as_view(), name='create_tournament'),
    path('events/create/save/', events_view.SaveEvent.as_view(), name='save_new_tournament'),
    path('events/<int:event_id>/', event_view.Event.as_view(), name='event'),
    path('events/<int:event_id>/join/', event_view.Event.as_view(), name='join_tournament'),
    path('events/<int:event_id>/unjoin/', event_view.EventUnjoin.as_view(), name='unjoin_tournament'),
    path('events/<int:event_id>/confirm/', event_view.ConfirmTeam.as_view(), name='confirm_team'),
    path('events/<int:event_id>/decline/', event_view.DeclineTeam.as_view(), name='decline_team'),
    path('events/<int:event_id>/generate-schedule/', event_view.GenerateSchedule.as_view(), name='generate_schedule'),

    path('results/', results_view.Results.as_view(), name='results'),
    path('results/<int:event_id>/', result_view.ResultEvent.as_view(), name='result_event'),
    path('results/<int:event_id>/save-results/', result_view.ResultEvent.as_view(), name='save_results'),
]