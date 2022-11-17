from django.views.generic import TemplateView
from django.shortcuts import render
from ..models import Tournament, TournamentType


# from django.core.validators import validate_email
# from django.core.exceptions import ValidationError

from ..models import RegisteredUser
from datetime import datetime

class Events(TemplateView):
    template_events_name = "main_app/events.html"

    def get(self, request):
        events = [
            {
                "info": Tournament(
                    id=1,
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
            },
            {
                "info": Tournament(
                    id=2,
                    name="test random Event",
                    description="m m mmm mm m m mmmm m m mm mmm m mm m mmmm mmmmm mmmmmm m m mmmm mm mmm mmm mm mm mmmmmmm mm mm .",
                    date=datetime.strptime("11/28/22 10:15:00", "%m/%d/%y %H:%M:%S"),
                    prize="$100",
                    type=None,#TournamentType(type="chess") id..,
                    state=1,
                    minimum_team_size=1,
                    maximum_team_size=5
                ),
                "type": "Drinking games"
            },
            {
                "info": Tournament(
                    id=3,
                    name="test Event2",
                    description="In this tournament, you have to...",
                    date=datetime.strptime("12/20/22 18:30:00", "%m/%d/%y %H:%M:%S"),
                    prize="$100",
                    type=None,#TournamentType(type="chess") id..,
                    state=1,
                    minimum_team_size=1,
                    maximum_team_size=5
                ),
                "type": "Table football"
            }
        ]
        args = {
            "events": events,
        }

        return render(request, self.template_events_name, args)
    