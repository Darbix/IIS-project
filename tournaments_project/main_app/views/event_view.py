from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from ..models import Tournament, TournamentType, Team, UserTournamentModerator, RegisteredUser, UserTeam
from datetime import datetime
from django.db.models import Q
from itertools import chain
from django.contrib import messages

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
            moderator_ids = list(UserTournamentModerator.objects.filter(tournament=event.id).values_list("id", flat=True))
        except:
            moderator_ids = None

        team = None # Current user's team joined in the tournament

        if(teams):
            try:
                # Load teams which contain a logged user to a list
                userteams_team_ids = list(UserTeam.objects.filter(user=request.session.get("user")["id"]).values_list("team", flat=True))
                if(userteams_team_ids):
                    # Find a team using userteam_team_ids which is joined in this tournament
                    team = teams.filter(tournament=event.id).get(id__in=userteams_team_ids)
            except:
                team = None
            
            unconfirmed_teams = []
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
            "teams": teams,
            "team": team,
            "owner_teams": owner_teams,
            "unconfirmed_teams": unconfirmed_teams
        }
            # "moderator_ids": moderator_ids
        return render(request, self.template_event_name, args)


    def post(self, request, *args, **kwargs):
        """ Join the tournament POST request """
        try:
            # Load the event
            event = Tournament.objects.get(id=kwargs["event_id"])
        except:
            # Event does not exist
            return redirect(self.events_page)

        # Decide between individual/team join
        if(request.POST["player_team"] == "player"):
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

        else:
            try:
                team = Team.objects.get(id=int(request.POST["player_team"]))

                # Get the users in this team
                user_ids = list(UserTeam.objects.filter(team=team.id).values_list("user", flat=True))
                users = RegisteredUser.objects.filter(id__in=user_ids)

                not_in_tournament = True
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

                if(team and not_in_tournament):
                    team.tournament = event
                    team.save()
                    
                    messages.info(request, "Your request to join the tournament was sent to its manager")
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

class GenerateSchedule(TemplateView):
    def post(self, request, *args, **kwargs):

        # TODO generate N / 2 matches + (N / 2) / 2 + ... with blank results 
        # Change a state to 'ongoing'
        # Save data to database, randomize teams, connect TournamentRounds (teans) and KnockoutTournaments (matches as winners)
        messages.info(request, "TODO, data are implicit")

        return redirect("result_event", event_id=kwargs["event_id"])