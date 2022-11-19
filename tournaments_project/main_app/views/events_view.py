from django.views.generic import TemplateView
from django.shortcuts import render
from ..models import Tournament, TournamentType
from django.db.models import Q

# from django.core.validators import validate_email
# from django.core.exceptions import ValidationError

from ..models import RegisteredUser
from datetime import datetime

class Events(TemplateView):
    template_events_name = "main_app/events.html"

    def get(self, request):
        tournaments = Tournament.objects.filter(~Q(state=0))
        args = {
            "events": tournaments,
        }
        return render(request, self.template_events_name, args)
