from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.contrib import messages
from ..models import RegisteredUser, Team, UserTeam, Tournament, KnockoutMatch, TournamentRound


class Stats(TemplateView):
    template_name = "main_app/stats.html"
    
    def get(self, request):
        players = []

        try:
            users = RegisteredUser.objects.all()

            for player in users:
                # Load all user's teams
                team_ids = list(UserTeam.objects.filter(user=player.id).values_list("team", flat=True))
                # Get all events the user is in (through a team)
                event_ids = list(Team.objects.filter(id__in=team_ids, confirmed=1).values_list("tournament", flat=True))
                # A number of events each user played
                events = Tournament.objects.filter(id__in=event_ids, state=3)

                n_matches = 0   # A number of played matches
                n_beaten = 0    # A number of beaten teams (won matches)
                n_wins = 0      # A number of tournament wins
            
                for team_id in team_ids:
                    round = None
                    # Load the starting team-match rows (TournamentRound)
                    try:
                        try:
                            round = TournamentRound.objects.get(team_1=team_id)
                            # If a team did not win the match, continue
                            if(round.match.team_1_score <= round.match.team_2_score):
                                n_matches += 1
                                # Check another team in an event
                                continue

                        except:
                            try: 
                                round = TournamentRound.objects.get(team_2=team_id)
                                # If a team did not win the match, continue
                                if(round.match.team_1_score >= round.match.team_2_score):
                                    n_matches += 1
                                    # Check another team in an event
                                    continue
                            except:
                                # Can be more teams, but this one is not in any tournament 
                                continue
                    except:
                        break
                    
                    # Move tha current match, because the team has won the first match
                    match_id = round.match
                    n_matches += 1
                    n_beaten += 1
                        
                    # While a KnockoutMatch with a team as a winner in it exists, load and count them
                    while(True):
                        try:
                            elim = KnockoutMatch.objects.get(team_1_match_winner=match_id)
                            # If a team did not win the match, continue
                            if(elim.match.team_1_score <= elim.match.team_2_score):
                                n_matches += 1
                                break
                        except:
                            try: 
                                elim = KnockoutMatch.objects.get(team_2_match_winner=match_id)
                                # If a team did not win the match, continue
                                if(elim.match.team_1_score >= elim.match.team_2_score):
                                    n_matches += 1
                                    break
                            except KnockoutMatch.DoesNotExist:
                                # The team won
                                n_wins += 1
                                break
                            except:
                                break
                        
                        n_matches += 1
                        n_beaten += 1
                        match_id = elim.match.id

                players.append({
                    "info": player, 
                    "n_events": len(list(events)), 
                    "n_matches": n_matches,
                    "perc_beaten": 0 if n_matches == 0 else 100.0 * n_beaten / n_matches,
                    "n_wins": n_wins,
                })
            
        except:
            messages.info(request, "Stats could not be loaded");
            players = []
        
        # Sort the final list in specified order
        players = sorted(players, key=lambda d: (d["n_wins"], d["perc_beaten"], d["n_matches"], d["n_events"]), reverse=True) 

        args = {
            "players": players
        }

        return render(request, self.template_name, args) 
    