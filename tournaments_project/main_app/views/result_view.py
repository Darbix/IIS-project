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
        
        try:
            teams = Team.objects.filter(tournament=event.id, confirmed=1)
            db_matches = TournamentMatch.objects.filter(tournament=event.id).order_by("id")
        except:
            teams = []
            db_matches = []
            
        matches = []
        teams_ordered = []
        m_cnt = 0

        try:
            for m in db_matches:
                pair = None # TournamentRound for a first row
                elim = None # KnockoutMatche cells in other than the first rows
                t1 = None   # First team
                t2 = None   # Second team

                # If a cell is a TournamentRound (first non team row connecting Teams), load the first 2 teams
                if(TournamentRound.objects.filter(match=m.id).exists()):
                    pair = TournamentRound.objects.get(match=m.id)
                    t1 = teams.get(id=pair.team_1.id)
                    t2 = teams.get(id=pair.team_2.id)
                    teams_ordered.append(t1)
                    teams_ordered.append(t2)

                # If a cell is a KnockoutMatch (all the rows connecting previous Matches as winners)
                elif(KnockoutMatch.objects.filter(match=m.id).exists()):
                    # Current knockout match
                    elim = KnockoutMatch.objects.get(match=m.id)

                    # Find a winner team from left matches
                    match = db_matches.get(id=elim.team_1_match_winner.id)
                    t1 = self.find_winner_team(db_matches, match)

                    # Find a winner team from right matches
                    match = db_matches.get(id=elim.team_2_match_winner.id)
                    t2 = self.find_winner_team(db_matches, match)

                matches.append({
                        "id": m.id, 
                        "t1_score": m.team_1_score, 
                        "t2_score": m.team_2_score, 
                        "t1": t1, 
                        "t2": t2
                    }
                )
                m_cnt += 1
        except:
            pass
        
        winner_team = None
        if(matches):
            try:
                # Get a tournament winner to display at the top
                winner_team = self.find_winner_team(db_matches, db_matches.get(id=matches[-1]["id"]))
            except:
                winner_team =  None
            
            if(winner_team):
                team_member_ids = list(UserTeam.objects.filter(team=winner_team.id).values_list("user", flat=True))
                members = RegisteredUser.objects.filter(id__in=team_member_ids)
                winner_team = {"info": winner_team, "members": members}
        
        try:
            # A list of moderators that can configure the event
            moderator_ids = list(UserTournamentModerator.objects.filter(tournament=event.id).values_list("user", flat=True))
        except:
            moderator_ids = None
    
        args = {
            "event": event,
            "teams": teams_ordered,
            "matches": matches,
            "moderator_ids": moderator_ids,
            "winner_team": winner_team
        }

        return render(request, self.template_result_event_name, args)

    
    def get_winner(self, match):
        """
        Get a winner from a single specific match
        @param match: Match where to find it's winner team
        @return: A Team that won the match
        """
        if(not match):
            return None
        sc1 = match.team_1_score
        sc2 = match.team_2_score
        pair = TournamentRound.objects.get(match=match.id)
        return pair.team_1 if sc1 > sc2 else (pair.team_2 if sc1 < sc2 else None)
    

    def find_winner_team(self, db_matches, match):
        """ 
        Iteratively find the team that won the match as KnockoutMatch
        @param db_matches: All the possible matches in the tournament to find in
        @param match: Match where to find it's winner team
        @return: A Team that won the match
        """
        e = None
        # While Knockout points to a Match and not TournamentRound (then get a winner)
        while(KnockoutMatch.objects.filter(match=match.id).exists()):
            if(match and match.team_1_score == match.team_2_score):
                match = None
                break
            e = KnockoutMatch.objects.get(match=match.id)
            match = db_matches.get(id=(e.team_1_match_winner.id if match.team_1_score > match.team_2_score else e.team_2_match_winner.id)) 
        return self.get_winner(match)

    
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
                        # Update the values in all selected matches 
                        if(str(match.id) in match_ids):
                            i = match_ids.index(str(match.id))
                            match.team_1_score = int(t1_scores[i])
                            match.team_2_score = int(t2_scores[i])
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
            
            if(not matches):
                messages.info(request, "There were no matches to remove")
            else:
                for match in matches:
                    match.delete()
            
                messages.info(request, "Scheduled matches were successfully deleted")
        except:
            messages.info(request, "The event was not found to clear the schedule")
        return redirect("result_event", event_id=kwargs["event_id"])
    