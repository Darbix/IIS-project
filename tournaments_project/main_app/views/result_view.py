from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.conf import settings
from itertools import chain
from django.db.models import Q
from django.contrib import messages
from PIL import Image
from pathlib import Path
from ..models import RegisteredUser, Team, UserTeam, Tournament, TournamentMatch

class ResultEvent(TemplateView):
    template_result_event_name = "main_app/result_event.html"

    def get(self, request, *args, **kwargs):
        event = None
        if(kwargs["event_id"]):
            try:
                event = Tournament.objects.get(id=kwargs["event_id"])
            except:
                event = None
        
        # TODO load data into dictionaries with just important information
        try:
            teams = [
                {"id": 1, "name": "TEAM_XY1"},
                {"id": 2, "name": "TEAM_XY2"},
                {"id": 3, "name": "TEAM_XY3"},
                {"id": 4, "name": "TEAM_XY4"},
                {"id": 5, "name": "TEAM_XY5"},
                {"id": 6, "name": "TEAM_XY6"},
                {"id": 7, "name": "TEAM_XY7"},
                {"id": 8, "name": "TEAM_XY8"},
            ]
            # Using TournamentRound (match, team1, team2) get ordered Matches and fill dictionaries
            matches = [
                # TournamentMatches
                {"id": 1, "t1_score": 1, "t2_score": 0, "t1": teams[0], "t2": teams[1]},
                {"id": 2, "t1_score": 0, "t2_score": 5, "t1": teams[2], "t2": teams[3]},
                {"id": 3, "t1_score": 6, "t2_score": 0, "t1": teams[4], "t2": teams[5]},
                {"id": 4, "t1_score": 3, "t2_score": 2, "t1": teams[6], "t2": teams[7]},
            ]
            matches = matches + [
                # KnockoutMatches, somehow get the winners from matches
                # Representing match winners as Teams, not previous Matches (in a dictionary sent to a template)
                {"id": 5, "t1_score": 8, "t2_score": 0, "t1": self.get_winner(matches[0]), "t2": self.get_winner(matches[1])},
                {"id": 6, "t1_score": 0, "t2_score": 0, "t1": self.get_winner(matches[2]), "t2": self.get_winner(matches[3])},
            ]

            matches = matches + [
                {"id": 7, "t1_score": 0, "t2_score": 0, "t1": self.get_winner(matches[4]), "t2": self.get_winner(matches[5])}
            ]

        except:
            pass

        args = {
            "event": event,
            "teams": teams,
            "matches": matches
        }

        return render(request, self.template_result_event_name, args)

    def get_winner(self, match):
        sc1 = match["t1_score"]
        sc2 = match["t2_score"]

        return match["t1"] if sc1 > sc2 else (match["t2"] if sc1 < sc2 else None)
    
    def post(self, request, *args, **kwargs):
        match_ids = request.POST.getlist("match_id")
        t1_scores = request.POST.getlist("t1_score")
        t2_scores = request.POST.getlist("t2_score")

        # TODO
        try:
            matches = TournamentMatch.objects.filter(tournament=kwargs["event_id"])
            if(matches):
                for match in matches:
                    try:
                        i = match_ids.index(match.id)
                        match.team_1_score = t1_scores[i]
                        match.team_2_score = t2_scores[i]
                        # match.save()
                    except:
                        messages.info(request, "Invalid match ID")
        except:
            messages.info(request, "Saving results failed")
            pass

        return redirect("result_event", event_id=kwargs["event_id"])
        
        