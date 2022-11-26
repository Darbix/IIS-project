from django.views.generic import TemplateView
from django.shortcuts import render, redirect

from ..models import RegisteredAdmin

from main_app import models as user_models

class Tournaments(TemplateView):
    template_name = 'admin_app/tournaments.html'
    template_name_single = 'admin_app/tournament.html'
    login_page = 'login'
    header = [ "{}".format(x.name) for x in user_models.Tournament._meta.fields ]

    def get(self, request, *args, **kwargs):
        if not RegisteredAdmin.IsLoggedIn(request):
            return redirect(self.login_page)

        if 'event_id' not in kwargs:
            return self.get_all(request)
        else:
            return self.get_single(request, kwargs['event_id'])

    def get_single(self, request, id):
        tournament = user_models.Tournament.objects.get(id=id)
        try:
            moderator = user_models.UserTournamentModerator.objects.get(tournament=id).user
        except:
            moderator = None
        teams = user_models.Team.objects.filter(tournament=id)
        team_users = user_models.UserTeam.objects.filter(team__in=teams)
        tournament_types = user_models.TournamentType.objects.all()

        teams_with_users = {}
        for team_user in team_users:
            if team_user.team not in teams_with_users:
                teams_with_users[team_user.team] = []
            teams_with_users[team_user.team].append(team_user.user)

        args = {
            'tournament': tournament,
            'moderator': moderator,
            'teams_with_users': teams_with_users,
            'tournament_types': tournament_types,
        }
        return render(request, self.template_name_single, args)

    def get_all(self, request):
        tournaments = user_models.Tournament.objects.all()

        # 2 query nebo filtrovat "ručně"?
        unconfirmed = user_models.Tournament.objects.filter(state=0)
        # unconfirmed = list([ t for t in tournaments if t.state == 0 ])

        args = {
            "header": self.header,
            "unconfirmed_tournaments": unconfirmed,
            "all_tournaments": tournaments
        }
        return render(request, self.template_name, args)
    
    def post(self, request, *args, **kwargs):
        if not RegisteredAdmin.IsLoggedIn(request):
            return redirect(self.login_page)
        
        if 'confirm' in request.POST and 'id' in request.POST:
            return self.postConfirm(request.POST['id'])
        elif 'event_id' in kwargs:
            if 'update' in request.POST:
                return self.postUpdate(request, kwargs['event_id'])
            elif 'delete' in request.POST:
                return self.postDelete(kwargs['event_id'])

        return redirect('tournaments')

    def postConfirm(self, id):
        try:
            tournament = user_models.Tournament.objects.get(id=id)
        except:
            # Turnaj neexistuje - nemělo by nastat
            return redirect('tournaments')

        tournament.state = 1
        tournament.save()

        return redirect('tournaments')

    def postUpdate(self, request, id):
        try:
            tournament = user_models.Tournament.objects.get(id=id)
        except:
            # Turnaj neexistuje - nemělo by nastat
            return redirect('tournaments')
        
        for field in user_models.Tournament._meta.local_fields:
            if field.name in request.POST and field.name != 'id' and field.name != 'state':
                setattr(tournament, field.name, request.POST[field.name])
        tournament.save()

        return redirect('tournaments')

    def postDelete(self, id):
        try:
            tournament = user_models.Tournament.objects.get(id=id)
        except:
            # Turnaj neexistuje - nemělo by nastat
            return redirect('tournaments')
        tournament.delete()

        return redirect('tournaments')
