from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.conf import settings
from itertools import chain
from django.db.models import Q
from ..models import RegisteredUser, Team, UserTeam, Tournament

class Teams(TemplateView):
    template_name = 'main_app/user_teams.html'

    def get(self, request):
        # TODO old teams

        try:
            # All the teams
            created_teams = Team.objects.filter(owner=request.session.get("user")["id"])
        except:
            created_teams = None
        
        try:
            # All the teams (ids) the user created
            team_ids = list(UserTeam.objects.filter(user=request.session.get("user")["id"]).values_list("team", flat=True))

            # TODO not tested
            # Get all teams a user is present in except those where the user is an owner 
            teams_with_user = Team.objects.filter(id__in=team_ids).filter(~Q(owner=request.session.get("user")["id"]))
        except:
            teams_with_user = None

        # Teams the logged in user owns
        own_teams = self.get_team_list(created_teams)

        # Teams the logged in user is in
        fellow_teams = self.get_team_list(teams_with_user)

        args = {
            "own_teams": own_teams,
            "fellow_teams": fellow_teams,
        }

        return render(request, self.template_name, args)

    def post(self, request):
        return render(request, self.template_name)


    def get_team_list(self, teams):
        """ Get a list model structures of teams, members and events where the teams are joined """
        # A list of team dictionaries with info
        result_teams = []
        if(teams):
            try:
                # Create a structure for each team with members
                for team in teams:
                    # Get member ids for each team and exclude the owner (current user)
                    team_member_ids = list(UserTeam.objects.filter(team=team.id).values_list("user", flat=True))
                    team_member_ids.remove(int(team.owner.id))

                    team_members = RegisteredUser.objects.filter(id__in=team_member_ids)
                    # Owner at the first place (should be a current user)
                    owner = RegisteredUser.objects.get(id=team.owner.id)
                    team_members = chain([owner], team_members)

                    try:
                        event = Tournament.objects.get(id=team.tournament.id)
                    except:
                        event = None

                    result_teams.append({
                        "info": team, 
                        "members": team_members,
                        "event": {"id":event.id, "name": event.name} if event else None
                    })
            except:
                result_teams = None

        return result_teams