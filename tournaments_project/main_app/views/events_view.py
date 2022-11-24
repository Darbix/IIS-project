from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from ..models import Tournament, TournamentType
from django.db.models import Q
from django.contrib import messages

# from django.core.validators import validate_email
# from django.core.exceptions import ValidationError

from ..models import RegisteredUser, UserTournamentModerator
from datetime import datetime

class Events(TemplateView):
    template_events_name = "main_app/events.html"

    def get(self, request):
        try:
            tournaments = Tournament.objects.filter(~Q(state=0))
        except:
            tournaments = None

        moderators_event_ids = []
        try:
            # A list of events where the current user is a moderator
            if(request.session.get("user")):
                moderators_event_ids = list(UserTournamentModerator.objects.filter(user=request.session.get("user")["id"]).values_list("tournament", flat=True))
        except:
            moderators_event_ids = []

        args = {
            "events": tournaments,
            "moderators_event_ids": moderators_event_ids
        }
        return render(request, self.template_events_name, args)

class EventCreate(TemplateView):
    template_event_create = "main_app/event_create.html"

    def get(self, request):
        game_types = list(TournamentType.objects.all())
        args = {
            "types": game_types
        }
        return render(request, self.template_event_create, args)

class SaveEvent(TemplateView):
    template_event_save = "main_app/events.html"
    events_page = "/events"

    def post(self, request):

        try:
            session_user = RegisteredUser.objects.get(id=request.session.get("user")["id"])
        except:
            session_user = None

        try:
            name_t = request.POST["name"]
            date_t = datetime.strptime(request.POST["date"], "%Y-%m-%dT%H:%M")
            type_t = TournamentType.objects.get(id=request.POST["type"])
            description_t = request.POST["description"]
            prize_t = request.POST["prize"]
            capacity_t = int(request.POST["capacity"])
            min_t = int(request.POST["min"])
            max_t = int(request.POST["max"])

            tournament = Tournament(name=name_t,
                                    date=date_t,
                                    type=type_t,
                                    state=0,
                                    description=description_t,
                                    prize=prize_t,
                                    capacity=capacity_t,
                                    minimum_team_size=min_t,
                                    maximum_team_size=max_t)
            tournament.save()
            messages.info(request, "Tournament was successfully created")
        except:
            messages.warning(request, "Tournament was not created")
            tournament = None

        try:
            tournament_moderator = UserTournamentModerator(user = session_user, tournament = tournament)
            tournament_moderator.save()
        except:
            tournament_moderator = None

        return redirect(self.events_page)

# TODO: 
# class EditEvent(TemplateView):
#     template_event_save = "main_app/events.html"

#     def post(self, request):

#         # # try:
#         tournament.name = request.POST["name"]
#         tournament.date = datetime.strptime(request.POST["date"], "%Y-%m-%d-%H-%M")
#         tournament.type = request.POST["type"]
#         tournament.description = request.POST["description"]
#         tournament.prize = request.POST["prize"]
#         tournament.capacity = int(request.POST["capacity"])
#         tournament.minimum_team_size = int(request.POST["min"])
#         tournament.maximum_team_size = int(request.POST["max"])
#         #     # tournament.save()
#         # messages.info(request, "The tournament was successfully edited")
#         # except:
#         #     messages.info(request, "The tournament was not edited")

#         return render(request, self.template_event_save)