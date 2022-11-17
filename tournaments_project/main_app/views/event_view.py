from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from ..models import Tournament, TournamentType, Team
from ..models import RegisteredUser
from datetime import datetime

class Event(TemplateView):
    template_event_name = "main_app/event.html"

    def get(self, request, *args, **kwargs):
        if("event_id" in kwargs):
            event = {
                "info": Tournament(
                    id=kwargs["event_id"], # TODO !!
                    name="FIT chess tournament for everybody",
                    description="In this tournament, you have to jedna dva tri lipsum lore jasd ha a aa sdk aa dva tri lipsum lore jasd ha a aa sdk ;a\
                        a dva tri lipsum lore jasd ha a aa sdk ;a 4 5 6 8 a dva tri lipsum lore jasd ha a aa sdk a\
                        dsadasd j j j j jiasd sad asdj apsdo hg a tri lipsum lore jasd ha a aa sdk a \
                        a dva tri lipsum lore j",
                    date=datetime.strptime("11/20/22 18:30:00", "%m/%d/%y %H:%M:%S"),
                    prize="$100",
                    type=None,#TournamentType(type="chess") id..,
                    state=1,
                    minimum_team_size=1,
                    maximum_team_size=5
                ),
                "type": "Board games"
            }

            members = RegisteredUser.objects.all()
            teams = [
                Team(
                    id=1,
                    name="Beasts",
                    owner=members[0]
                )
            ]

            args = {
                "event": event,
                "members": members,
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