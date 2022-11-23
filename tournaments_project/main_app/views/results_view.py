from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.conf import settings
from itertools import chain
from django.db.models import Q
from django.contrib import messages
from PIL import Image
from pathlib import Path
from ..models import RegisteredUser, Team, UserTeam, Tournament

class Results(TemplateView):
    template_name = "main_app/results.html"

    def get(self, request):
        # Prepared events with knockout schedules
        ongoing_events = Tournament.objects.filter(state=2)
        # Finished events with results
        finished_events = Tournament.objects.filter(state=3)

        args = {
            "ongoing_events": ongoing_events,
            "finished_events": finished_events
        }

        return render(request, self.template_name, args)
    