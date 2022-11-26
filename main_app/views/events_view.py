from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from ..models import Tournament, TournamentType
from django.db.models import Q
from django.contrib import messages
from ..models import RegisteredUser, UserTournamentModerator
from datetime import datetime

class Events(TemplateView):
    template_events_name = "main_app/events.html"

    def get(self, request):
        tournaments = []
        moderators_event_ids = []

        try:
            tournaments = Tournament.objects.filter(state__in=[1,2]).order_by("date")
        except:
            tournaments = []

        moderators_event_ids = []
        try:
            # A list of events where the current user is a moderator
            if(request.session.get("user")):
                moderators_event_ids = list(UserTournamentModerator.objects.filter(user=request.session.get("user")["id"]).values_list("tournament", flat=True))

            # A user is a moderator in some tournaments and has to be able to see them even when they are unconfirmed
            if(moderators_event_ids):
                tournaments = tournaments | Tournament.objects.filter(state=0, id__in=moderators_event_ids)
                tournaments = tournaments.order_by("date")
        except:
            moderators_event_ids = []

        args = {
            "events": tournaments,
            "moderators_event_ids": moderators_event_ids
        }
        return render(request, self.template_events_name, args)

class EventCreate(TemplateView):
    template_event_create = "main_app/event_create.html"
    events_page = "events"

    def get(self, request, *args, **kwargs):
        event = None
        try:
            # Load an existing event, if it is Edit and not Create
            if("event_id" in kwargs):
                event = Tournament.objects.get(id=kwargs["event_id"])
        except:
            messages.info(request, "Incorrect event")
            return redirect(self.events_page)

        game_types = list(TournamentType.objects.all())
        args = {
            "event": event,
            "types": game_types
        }
        return render(request, self.template_event_create, args)

class SaveEvent(TemplateView):
    template_event_save = "main_app/events.html"
    events_page = "/events"

    def post(self, request):
        if(not request.session.get("user")):
            messages.info(request, "You must be logged in to create tournaments")
            return redirect(self.events_page)

        event = None
        if("event_id" in request.POST):
            try:
                # Existing event will be changed or a new one created
                event = Tournament.objects.get(id=int(request.POST["event_id"]))
                moderator_ids = list(UserTournamentModerator.objects.filter(tournament=event.id).values_list("user", flat=True))
                
                if(request.session.get("user")["id"] not in moderator_ids):
                    event = None
            except:
                event = None
            if(not event):
                messages.info(request, "Event edit failed")
                return redirect(self.events_page)

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
            state_t = 0

            if(capacity_t % 2 != 0 or capacity_t <= 0):
                messages.info(request, "The capacity must be an even number > 0")
            if(min_t > max_t or min_t <= 0 or max_t <= 0):
                messages.info(request, "Invalid Min or Max value")
            else:     
                tournament = Tournament()
                if(event):  
                    state_t = event.state
                    tournament = event     
                    
                tournament.name = name_t
                tournament.date = date_t
                tournament.type = type_t
                tournament.state = state_t
                tournament.description = description_t
                tournament.prize = prize_t
                tournament.capacity = capacity_t
                tournament.minimum_team_size = min_t
                tournament.maximum_team_size = max_t

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