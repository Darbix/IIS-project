from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from ..models import Tournament, TournamentType, Team, UserTournamentModerator, RegisteredUser, UserTeam
from datetime import datetime
from django.db.models import Q
from itertools import chain

class Event(TemplateView):
    events_page = "events"
    template_event_name = "main_app/event.html"

    def get(self, request, *args, **kwargs):
        try:
            event = Tournament.objects.get(id=kwargs["event_id"])
        except:
            # Neexistující turnaj
            return redirect(self.events_page)
        
        # Správce turnaje
        try:
            moderator = UserTournamentModerator.objects.filter(tournament=event)
        except:
            moderator = None

        # Týmy účastníci se tohoto turnaje
        try:
            teams = Team.objects.filter(tournament=event)
        except:
            teams = None

        try:
            # All current user's teams
            owner_teams = Team.objects.filter(owner=request.session.get("user")["id"])
        except:
            owner_teams = None

        team = None # Current user's team joined in the tournament

        if(teams):
            try:
                team = teams.get(owner=request.session.get("user")["id"])
            except:
                team = None
            
            if(team):
                teams = teams.filter(~Q(id=team.id))
                try:
                    # Get team member ids
                    members_ids = list(UserTeam.objects.filter(team=team.id).values_list("user", flat=True))
                    # Exclude the owner to place it to the list start
                    members_ids.remove(int(team.owner.id))
                    owner = RegisteredUser.objects.get(id=team.owner.id)
                    
                    members = None
                    if(members_ids):
                        members = RegisteredUser.objects.filter(id__in=members_ids)
                        members = chain([owner], members)
                    else:
                        members = [owner]
                    team = {"info": team, "members": members}
                except:
                    pass

        args = {
            "event": event,
            "moderator": moderator,
            "teams": teams,
            "team": team,
            "owner_teams": owner_teams
        }
        return render(request, self.template_event_name, args)

    def post(self, request, *args, **kwargs):
        print(request, "JOIN", request.POST["player_team"])
        # TODO if value == "player" (generate a team for him?) else => team id

        return redirect("event", event_id=kwargs["event_id"])

class EventUnjoin(TemplateView):
    def post(self, request, *args, **kwargs):
        print(request, "UNJOIN")

        return redirect("event", event_id=kwargs["event_id"])