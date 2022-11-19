from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from ..models import Tournament, TournamentType, Team, UserTournamentModerator, RegisteredUser
from datetime import datetime

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
        
        args = {
            "event": event,
            "moderator": moderator,
            "teams": teams
        }
        return render(request, self.template_event_name, args)

    def post(self, request, *args, **kwargs):
        print(request, "JOIN", request.POST["player_team"])

        return redirect("event", event_id=kwargs["event_id"])

class EventUnjoin(TemplateView):
    def post(self, request, *args, **kwargs):
        print(request, "UNJOIN")

        return redirect("event", event_id=kwargs["event_id"])