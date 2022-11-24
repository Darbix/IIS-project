from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.conf import settings
from itertools import chain
from django.db.models import Q
from django.contrib import messages
from PIL import Image
from pathlib import Path
from ..models import RegisteredUser, Team, UserTeam, Tournament, TournamentMatch, UserTournamentModerator, TournamentRound, KnockoutMatch

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
        # try:
            # teams = [
            #     {"id": 1, "name": "TEAM_XY1"},
            #     {"id": 2, "name": "TEAM_XY2"},
            #     {"id": 3, "name": "TEAM_XY3"},
            #     {"id": 4, "name": "TEAM_XY4"},
            #     {"id": 5, "name": "TEAM_XY5"},
            #     {"id": 6, "name": "TEAM_XY6"},
            #     {"id": 7, "name": "TEAM_XY7"},
            #     {"id": 8, "name": "TEAM_XY8"},
            # ]
            # # Using TournamentRound (match, team1, team2) get ordered Matches and fill dictionaries
            # matches = [
            #     # TournamentMatches
            #     {"id": 1, "t1_score": 1, "t2_score": 0, "t1": teams[0], "t2": teams[1]},
            #     {"id": 2, "t1_score": 0, "t2_score": 5, "t1": teams[2], "t2": teams[3]},
            #     {"id": 3, "t1_score": 6, "t2_score": 0, "t1": teams[4], "t2": teams[5]},
            #     {"id": 4, "t1_score": 3, "t2_score": 2, "t1": teams[6], "t2": teams[7]},
            # ]
            # matches = matches + [
            #     # KnockoutMatches, somehow get the winners from matches
            #     # Representing match winners as Teams, not previous Matches (in a dictionary sent to a template)
            #     {"id": 5, "t1_score": 8, "t2_score": 0, "t1": self.get_winner(matches[0]), "t2": self.get_winner(matches[1])},
            #     {"id": 6, "t1_score": 0, "t2_score": 0, "t1": self.get_winner(matches[2]), "t2": self.get_winner(matches[3])},
            # ]

            # matches = matches + [
            #     {"id": 7, "t1_score": 0, "t2_score": 0, "t1": self.get_winner(matches[4]), "t2": self.get_winner(matches[5])}
            # ]
        teams = Team.objects.filter(tournament=event.id, confirmed=1)
        db_matches = TournamentMatch.objects.filter(tournament=event.id).order_by("id")

        matches = []
        teams_ordered = []
        m_cnt = 0
        m_pos = 0
        for m in db_matches:
            pair = None
            elim = None
            t1 = None
            t2 = None

            # if(m_cnt < int(len(teams) / 2)):
            if(TournamentRound.objects.filter(match=m.id).exists()):
                pair = TournamentRound.objects.get(match=m.id)
                t1 = teams.get(id=pair.team_1.id)
                t2 = teams.get(id=pair.team_2.id)
                teams_ordered.append(t1)
                teams_ordered.append(t2)

            elif(KnockoutMatch.objects.filter(match=m.id).exists()):
                # if(not teams_ordered):
                #     for x in matches:
                #         pair = TournamentRound.objects.get(match=match.id)
                #         teams_ordered.append(pair.team_1)
                #         teams_ordered.append(pair.team_2)

                elim = KnockoutMatch.objects.get(match=m.id)
                # t1 = db_matches.get(id=elim.team_1_match_winner.id)
                # t2 = db_matches.get(id=elim.team_2_match_winner.id)
                # print(elim.team_1_match_winner)
                match = db_matches.get(id=elim.team_1_match_winner.id)
                e = elim
                # While KO points to match (-> KO) not team (-> pair)
                while(KnockoutMatch.objects.filter(match=match.id).exists()):
                    if(match and match.team_1_score == 0 and match.team_2_score == 0):
                        match = None
                        break
                    e = KnockoutMatch.objects.get(match=match.id)
                    match = db_matches.get(id=(e.team_1_match_winner.id if match.team_1_score > match.team_2_score else e.team_2_match_winner.id)) 
                    # ne 1, ale rozhodnout, kdo je tam winner v db je co vychozi??
                t1 = self.get_winner_id(match) # TODO ne az na konci hledani.. nebo jo? 

                match = db_matches.get(id=elim.team_2_match_winner.id)
                e = elim
                # While KO points to match (-> KO) not team (-> pair)
                while(KnockoutMatch.objects.filter(match=match.id).exists()):
                    if(match and match.team_1_score == 0 and match.team_2_score == 0):
                        match = None
                        break
                    e = KnockoutMatch.objects.get(match=match.id)
                    match = db_matches.get(id=(e.team_1_match_winner.id if match.team_1_score > match.team_2_score else e.team_2_match_winner.id)) 
                t2 = self.get_winner_id(match)

            matches.append({
                    "id": m.id, 
                    "t1_score": m.team_1_score, 
                    "t2_score": m.team_2_score, 
                    "t1": t1, 
                    "t2": t2
                }
            )
            m_cnt += 1
        
        # except:
        #     pass
        
        try:
            # A list of moderators that can configure the event
            moderator_ids = list(UserTournamentModerator.objects.filter(tournament=event.id).values_list("user", flat=True))
        except:
            moderator_ids = None
    
        args = {
            "event": event,
            "teams": teams_ordered,
            "matches": matches,
            "moderator_ids": moderator_ids
        }

        return render(request, self.template_result_event_name, args)

    def get_winner_id(self, match):
        # sc1 = match["t1_score"]
        # sc2 = match["t2_score"]
        # return match["t1"] if sc1 > sc2 else (match["t2"] if sc1 < sc2 else None)

        if(not match):
            return None
        sc1 = match.team_1_score
        sc2 = match.team_2_score
        pair = TournamentRound.objects.get(match=match.id)
        return pair.team_1 if sc1 > sc2 else (pair.team_2 if sc1 < sc2 else None)
    

class SaveResults(TemplateView):

    def post(self, request, *args, **kwargs):
        match_ids = request.POST.getlist("match_id")
        t1_scores = request.POST.getlist("t1_score")
        t2_scores = request.POST.getlist("t2_score")

        try:
            matches = TournamentMatch.objects.filter(tournament=kwargs["event_id"])
            if(matches):
                for match in matches:
                    try:
                        if(str(match.id) in match_ids):
                            i = match_ids.index(str(match.id))
                            match.team_1_score = t1_scores[i]
                            match.team_2_score = t2_scores[i] #TODO only +int
                            match.save()
                        else:
                            # Blank match yet
                            continue
                    except:
                        messages.info(request, "Invalid match ID")
        except:
            messages.info(request, "Saving results failed")
            pass

        return redirect("result_event", event_id=kwargs["event_id"])
        
    
class EraseSchedule(TemplateView):
    def post(self, request, *args, **kwargs):
        try:
            matches = TournamentMatch.objects.filter(tournament=kwargs["event_id"])
            for match in matches:
                match.delete()
            
            messages.info(request, "Scheduled matches were successfully deleted")
        except:
            messages.info(request, "The event was not found to clear the schedule")
        return redirect("result_event", event_id=kwargs["event_id"])