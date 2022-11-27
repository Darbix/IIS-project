from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from ..models import Tournament, Team, UserTournamentModerator, RegisteredUser, UserTeam, TournamentMatch, TournamentRound, KnockoutMatch
from django.db.models import Q
from itertools import chain
from django.contrib import messages
import random

class Event(TemplateView):
    events_page = "events"
    template_event_name = "main_app/event.html"

    def get(self, request, *args, **kwargs):
        try:
            event = Tournament.objects.get(id=kwargs["event_id"])
        except:
            # Event does not exist
            return redirect(self.events_page)

        # Contestant teams
        try:
            teams = Team.objects.filter(tournament=event)
        except:
            teams = None

        try:
            # All free current user's teams
            owner_teams = Team.objects.filter(owner=request.session.get("user")["id"]).filter(tournament=None)
        except:
            owner_teams = None

        try:
            # A list of moderators that can confirm the joining teams
            moderator_ids = list(UserTournamentModerator.objects.filter(tournament=event.id).values_list("user", flat=True))
        except:
            moderator_ids = None

        team = None             # Current user's team joined in the tournament
        unconfirmed_teams = []  # Unconfirmed teams for moderators
        joined_teams = []       # Teams in the tournament in the list-model form dict with members

        if(teams):
            try:
                # Load teams which contain a logged user to a list
                userteams_team_ids = list(UserTeam.objects.filter(user=request.session.get("user")["id"]).values_list("team", flat=True))
                if(userteams_team_ids):
                    # Find a team using userteam_team_ids which is joined in this tournament
                    team = teams.filter(tournament=event.id).get(id__in=userteams_team_ids)
            except:
                team = None
            
            try:
                if(request.session.get("user") and moderator_ids):
                    if(request.session.get("user")["id"] in moderator_ids):
                        unconf_teams = teams.filter(confirmed=0)

                        for t in unconf_teams:
                            members_ids = list(UserTeam.objects.filter(team=t.id).values_list("user", flat=True))
                            members = None
                            if(members_ids):
                                members = RegisteredUser.objects.filter(id__in=members_ids)
                            unconfirmed_teams.append({"info": t, "members": members})
            except:
                pass

            teams = teams.filter(confirmed=1)

            try:
                # Normal people do not see unconfirmed contestant teams 
                teams = teams.filter(confirmed=1)
        
                if(team and teams):
                    # Other contestant team list should not contain user's team
                    teams = teams.filter(~Q(id=team.id)).order_by("confirmed")
                
                    # TODO check it
                for t in teams:
                    members_ids = list(UserTeam.objects.filter(team=t.id).values_list("user", flat=True))
                    members = None
                    if(members_ids):
                        members = RegisteredUser.objects.filter(id__in=members_ids)
                    joined_teams.append({"info": t, "members": members})

                if(team):
                    # Get team member ids
                    members_ids = list(UserTeam.objects.filter(team=team.id).values_list("user", flat=True))
                    # Exclude the owner to place it to the list start
                    members_ids.remove(int(team.owner.id))
                    owner = RegisteredUser.objects.get(id=team.owner.id)
                    
                    members = None
                    if(members_ids):
                        members = RegisteredUser.objects.filter(id__in=members_ids)
                        members = chain([owner], members)
                    else:
                        members = [owner]

                    team = {"info": team, "members": members}
            except:
                pass
        
        try:
            # Calculate free capacity in the tournament
            event.capacity = str(event.capacity - Team.objects.filter(tournament=event, confirmed=1).count()) + " / " + str(event.capacity)
        except:
            pass

        args = {
            "event": event,
            "moderator_ids": moderator_ids,
            "teams": joined_teams,
            "team": team,
            "owner_teams": owner_teams,
            "unconfirmed_teams": unconfirmed_teams
        }

        return render(request, self.template_event_name, args)


    def post(self, request, *args, **kwargs):
        """ Join the tournament POST request """
        try:
            # Load the event
            event = Tournament.objects.get(id=kwargs["event_id"])
        except:
            # Event does not exist
            return redirect(self.events_page)

        # Decide between individual/team join if redirection was not from the result page
        if("player_team" in request.POST and request.POST["player_team"] == "player"):
            not_in_tournament = True
            try:
                # Check if the user is not in a team in this tournament
                userteams_team_ids = list(UserTeam.objects.filter(user=request.session.get("user")["id"]).values_list("team", flat=True))
                if(userteams_team_ids):
                    # Find all teams in this tournament which contain the user
                    teams_with_user = Team.objects.filter(tournament=event.id).filter(id__in=userteams_team_ids)

                    if(teams_with_user.count() > 0):
                        not_in_tournament = False
            except:
                not_in_tournament = False
                messages.info(request, "There were some problems checking your presence in this tournament")

            if(not_in_tournament):
                try:
                    default_name = request.session.get("user")["first_name"] + "'s Team"
                    team_owner = RegisteredUser.objects.get(id=request.session.get("user")["id"])

                    # Prepare a team with a single player
                    new_team = Team(name=default_name, owner=team_owner, tournament=None)
                    # Prepare an owner to be added
                    player_owner = RegisteredUser.objects.get(id=request.session.get("user")["id"])
                except:
                    new_team = None
                    player_owner = None


                if(new_team and player_owner):
                    try:
                        # The team must be in database to be able to connect a UserTeam object
                        new_team.tournament = event
                        new_team.save()
                        userteam = UserTeam(user=player_owner, team=new_team)
                    except:
                        userteam = None
                    
                    if(userteam):
                        userteam.save()
                        messages.info(request, "You were added to the tournament")
                    else:
                        new_team.delete()
                        messages.info(request, "Error: You were not added to the tournament")
                else:
                    messages.info(request, "Team creation failed, you were not added to the tournament")
            else:
                messages.info(request, "You already are in this tournament")

        elif("player_team" in request.POST):
            try:
                team = Team.objects.get(id=int(request.POST["player_team"]))

                if(team):
                    # Get the users in this team
                    user_ids = list(UserTeam.objects.filter(team=team.id).values_list("user", flat=True))
                    users = RegisteredUser.objects.filter(id__in=user_ids)

                    not_in_tournament = True

                    if(users and users.count() <= event.maximum_team_size and users.count() >= event.minimum_team_size):
                        # Check if all users are not in this tournament yet
                        for user in users:
                            userteams_team_ids = list(UserTeam.objects.filter(user=user.id).values_list("team", flat=True))
                            
                            if(userteams_team_ids):
                                # Find all teams in this tournament which contain the user
                                teams_with_user = Team.objects.filter(tournament=event.id).filter(id__in=userteams_team_ids)

                                if(teams_with_user.count() > 0):
                                    not_in_tournament = False
                                    messages.info(request, "The user " + user.first_name + " " + user.last_name + " is already in this tournament")
                                    break

                        if(not_in_tournament):
                            team.tournament = event
                            team.save()
                            
                            messages.info(request, "Your request to join the tournament was sent to its manager")
                    else:
                        messages.info(request, "Your team has a wrong number of players")
            except:
                messages.info(request, "Cannot join the tournament")
                pass

        return redirect("event", event_id=kwargs["event_id"])

    
class EventUnjoin(TemplateView):
    def post(self, request, *args, **kwargs):
        try:
            # Load a team which contains a logged user
            userteam = UserTeam.objects.get(user=request.session.get("user")["id"], team=int(request.POST["team_id"]))
            if(userteam):
                try:
                    # The team must be in the tournament and the user has to be its owner
                    team = Team.objects.filter(tournament=kwargs["event_id"], owner=request.session.get("user")["id"]).get(id=userteam.team.id)

                    if(team):
                        team.tournament = None
                
                    team.save()
                    messages.info(request, "The team successfully left the tournament")
                except:
                    messages.info(request, "You are not an owner of this team")
        except:
            messages.info(request, "Tournament unjoin failed")
            pass

        return redirect("event", event_id=kwargs["event_id"])

    
class ConfirmTeam(TemplateView):
    def post(self, request, *args, **kwargs):
        try:
            event = Tournament.objects.get(id=kwargs["event_id"])
            free_capacity = event.capacity - Team.objects.filter(tournament=event, confirmed=1).count()

            if(free_capacity > 0):
                team = Team.objects.get(id=int(request.POST["team_id"]))
                team.confirmed = 1
                team.save()
                messages.info(request, "The team was successfully confirmed")
            else:
                messages.info(request, "Resize the event capacity to add more teams")
        except:
            messages.info(request, "The team confirmation failed")

        return redirect("event", event_id=kwargs["event_id"])

    
class DeclineTeam(TemplateView):
    def post(self, request, *args, **kwargs):
        try:
            event = Tournament.objects.get(id=kwargs["event_id"])

            if(event):
                moderator_ids = list(UserTournamentModerator.objects.filter(tournament=event.id).values_list("id", flat=True))

                if(request.session.get("user") and request.session.get("user")["id"] in moderator_ids):
                    team = Team.objects.get(id=int(request.POST["team_id"]))
                    team.tournament = None
                    team.save()

                    messages.info(request, "The team was successfully declined")
                else:
                    messages.info(request, "You are not authorized to decline this team")
        except:
            messages.info(request, "The team refusal failed")

        return redirect("event", event_id=kwargs["event_id"])

    
class RemoveTournament(TemplateView):
    def post(self, request, *args, **kwargs):
        try:
            event = Tournament.objects.get(id=kwargs["event_id"])
        except:
            messages.info(request, "The event does not exist")
            return redirect("event", event_id=kwargs["event_id"])
        
        # event.delete() TODO uncomment

        messages.info(request, "The tournament was successfully removed")
        return redirect("events")


class GenerateSchedule(TemplateView):
    def post(self, request, *args, **kwargs):
        try:
            event = Tournament.objects.get(id=kwargs["event_id"])
        except:
            messages.info(request, "The event does not exist")
            return redirect("event", event_id=kwargs["event_id"])

        # Remove existing matches
        try:
            matches = TournamentMatch.objects.filter(tournament=kwargs["event_id"])
            for match in matches:
                match.delete()
            
            messages.info(request, "Existing matches were successfully deleted")
        except:
            pass
        
        try:
            teams = list(Team.objects.filter(tournament=kwargs["event_id"], confirmed=1))
            # Shuffle the team for later pairs
            random.shuffle(teams)

            if(len(teams) % 2 != 0 and len(teams) != 0):
                messages.info(request, "A number of teams is not even")
                return redirect("event", event_id=kwargs["event_id"])

            # Create len(teams) / 2 matches for all pairs
            matches = [TournamentMatch(tournament=event, state=1, team_1_score=0, team_2_score=0) for _ in range(int(len(teams) / 2))]
            pairs = [TournamentRound(match=matches[int(i / 2)], team_1=teams[i], team_2=teams[i+1]) for i in range(0, len(teams), 2)]

        except:
            messages.info(request, "Team loading failed")
            return redirect("event", event_id=kwargs["event_id"])
        
        try:
            n = len(matches)        # A Number of matches in a previous row 
            m_cnt = len(matches)    # An index skip for matches to get the current ones
            m_pos = 0               # An index of the first match (winner) from a previous row
            elims = []              # A list of elimination matches KnockoutMatch

            # While the previous row has more that 1 matches
            while(n > 1):
                matches += [TournamentMatch(tournament=event, state=1, team_1_score=0, team_2_score=0) for _ in range(int(n / 2))]
                # Elimination match get the Match id, and team winners from the previous matches starting at (m_pos + i) in matches
                elims += [
                    KnockoutMatch(match=matches[m_cnt + int(i / 2)], 
                        team_1_match_winner=matches[m_pos + i], 
                        team_2_match_winner=matches[m_pos + i + 1]) 
                    for i in range(0, n, 2)
                ]

                m_pos = m_cnt        # Move the starting point to find winners from matches
                m_cnt = len(matches) # A number of all matches
                n = int(n / 2)       # A number of matches in the current row 
        except:
            messages.info(request, "Schedule generation unexpectedly failed")

        if(matches and pairs):
            try:
                for match in matches:
                    match.save() 
                for pair in pairs:
                    pair.save() 
                if(elims):
                    for elim in elims:
                        elim.save() 
            except:
                messages.info(request, "Schedule generation failed")

        messages.info(request, "The tournament schedule was randomly generated")
        return redirect("result_event", event_id=kwargs["event_id"])

    
class ChangeState(TemplateView):
    def post(self, request, *args, **kwargs):
        try:
            event = Tournament.objects.get(id=kwargs["event_id"])
            if(event):
                # Cannot change to unconfirmed and cannot change to confirmed from unconfirmed
                if(int(request.POST["state"]) == 0 or (int(request.POST["state"]) == 1 and event.state == 0)):
                    messages.info(request, "You cannot change the state to this option")
                else:
                    event.state = int(request.POST["state"])
                    event.save()

                    messages.info(request, "The event state was changed")
        except:
            messages.info(request, "The event does not exist")

        return redirect("event", event_id=kwargs["event_id"])
    