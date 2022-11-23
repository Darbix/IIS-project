from django.views.generic import TemplateView
from django.shortcuts import render
from ..models import Tournament, TournamentType
from django.db.models import Q

# from django.core.validators import validate_email
# from django.core.exceptions import ValidationError

from ..models import RegisteredUser, UserTournamentModerator
from datetime import datetime

class Events(TemplateView):
    template_events_name = "main_app/events.html"

    def get(self, request):
        tournaments = Tournament.objects.filter(~Q(state=0))

        try:
            # A list of events where the current user is a moderator
            if(request.session.get("user")):
                moderators_event_ids = list(UserTournamentModerator.objects.filter(user=request.session.get("user")["id"]).values_list("tournament", flat=True))
        except:
            moderators_event_ids = None

        args = {
            "events": tournaments,
            "moderators_event_ids": moderators_event_ids
        }
        return render(request, self.template_events_name, args)
