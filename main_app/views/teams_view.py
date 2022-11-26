from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.conf import settings
from itertools import chain
from django.db.models import Q
from django.contrib import messages
from PIL import Image
from pathlib import Path
from ..models import RegisteredUser, Team, UserTeam, Tournament

USER_TEAMS = "user_teams"

class Teams(TemplateView):
    template_name = "main_app/user_teams.html"
    page_not_found = "page_not_found.html"

    def get(self, request):
        if(not request.session.get("user")):
            return render(request, self.page_not_found)

        try:
            # Event ids which haven't started yet, so the teams can still be changed
            event_ids = list(Tournament.objects.filter(state__in=[0,1]).values_list("id", flat=True))
        except:
            event_ids = []

        try:
            # All the teams a user owns
            created_teams = Team.objects.filter(owner=request.session.get("user")["id"])

            created_teams = created_teams.filter(Q(tournament__in=event_ids) | Q(tournament__isnull=True))
        except:
            created_teams = None
        
        try:
            # All the teams (ids) containing a user
            team_ids = list(UserTeam.objects.filter(user=request.session.get("user")["id"]).values_list("team", flat=True))

            # Get all teams a user is present in except those where the user is an owner 
            teams_with_user = Team.objects.filter(id__in=team_ids).filter(~Q(owner=request.session.get("user")["id"]))

            teams_with_user = teams_with_user.filter(Q(tournament__in=event_ids) | Q(tournament__isnull=True))
        except:
            teams_with_user = None

        # Teams the logged in user owns
        own_teams = self.get_team_list(created_teams)

        # Teams the logged in user is in
        fellow_teams = self.get_team_list(teams_with_user)

        args = {
            "own_teams": own_teams,
            "fellow_teams": fellow_teams,
        }

        return render(request, self.template_name, args)


    def get_team_list(self, teams):
        """ Get a list model structures of teams, members and events where the teams are joined """
        # A list of team dictionaries with info
        result_teams = []
        if(teams):
            try:
                    # Create a structure for each team with members
                for team in teams:
                    # Get member ids for each team and exclude the owner (current user)
                    team_member_ids = list(UserTeam.objects.filter(team=team.id).values_list("user", flat=True))
                    
                    event = None
                    team_members = None
                    # UserTeam may not exist, if added through Admin
                    if(team_member_ids):
                        team_member_ids.remove(int(team.owner.id))

                        team_members = RegisteredUser.objects.filter(id__in=team_member_ids)
                        # Owner at the first place (should be a current user)
                        owner = RegisteredUser.objects.get(id=team.owner.id)
                        team_members = chain([owner], team_members)

                    try:
                        event = Tournament.objects.get(id=team.tournament.id)
                    except:
                        event = None

                    result_teams.append({
                        "info": team, 
                        "members": team_members,
                        "event": {"id":event.id, "name": event.name} if event else None
                    })
            except:
                result_teams = None

        return result_teams

class ChangeName(TemplateView):
    user_teams = USER_TEAMS

    def post(self, request):
        try:
            # Get a user's team (has to be an owner)
            team = Team.objects.get(id=int(request.POST["team_id"]))
            if(team.owner.id != request.session.get("user")["id"]):
                messages.info(request, "You are not authorized to change the team name")
                team = None
        except:
            messages.info(request, "A team does not exist")
            team = None

        if(team):
            try:
                team.name = request.POST["team_name"]
                team.save()
                messages.info(request, "The team name was changed")
            except:
                messages.info(request, "The team name could not be changed")

        return redirect(self.user_teams)

class TeamImageUpload(TemplateView):
    user_teams = USER_TEAMS

    def post(self, request):
        file = request.FILES.get("avatar")
        team_id = request.POST["team_id"]
        if not file or not team_id:
            messages.info(request, "Data receive problem occured or the team does not exist")
            return redirect(self.user_teams)

        try:
            # user = RegisteredUser.objects.get(id=session_user["id"])
            team = Team.objects.get(id=request.POST["team_id"])
        except RegisteredUser.DoesNotExist as _:
            messages.info(request, "The team is not valid")
            return redirect(self.user_teams)

        # Team logo path
        file_path = "/static/avatars/t" + str(team.id) + ".png"
        new_path = str(settings.BASE_DIR) + file_path

        try:
            im = Image.open(file)
            im.resize((256, 256))
            im.save(Path(new_path), "PNG")
        except Exception as e:
            messages.info(request, "Invalid image")
            return redirect(self.user_teams)
        team.avatar = file_path
        team.save()
        messages.info(request, "The team image was saved")

        response = redirect(self.user_teams)
        return response

class AddTeammate(TemplateView):
    user_teams = USER_TEAMS
    
    def post(self, request):
        try:
            # Get a player to be added
            player = RegisteredUser.objects.get(email=request.POST["email"])
        except:
            messages.info(request, "A user with this email does not exist")
            player = None
        
        try:
            # Get a user's team (has to be an owner)
            team = Team.objects.get(id=int(request.POST["team_id"]))
            if(team.owner.id != request.session.get("user")["id"]):
                messages.info(request, "You are not authorized to add players to this team")
                team = None
        except:
            messages.info(request, "A team does not exist")
            team = None

        # Create a UserTeam object to join a player to the team
        userteam = None
        not_in_tournament = True
        if(team and player):
            # TODO must not be in the tournament if the team is, yet
            if(team.tournament != None):
                try:
                    userteams_team_ids = list(UserTeam.objects.filter(user=player.id).values_list("team", flat=True))
                    if(userteams_team_ids):
                        # Find all teams which contain the user in the same tournament
                        teams_with_user = Team.objects.filter(tournament=team.tournament.id).filter(id__in=userteams_team_ids)

                        # If a user already is in the same tournament, do not add
                        if(teams_with_user.count() > 0):
                            not_in_tournament = False
                            messages.info(request, "The user is already in the same tournament and cannot be added to the team")
                except:
                    pass

            if(not_in_tournament):
                try:
                    userteam = UserTeam(user=player, team=team)
                    # Team must be again unconfirmed, so the manager can check the player count
                    team.confirmed = 0
                except:
                    userteam = None
        
        if(userteam):
            try:
                userteam.save()
                team.save()
                messages.info(request, "The user was added to your team")
            except:
                messages.info(request, "The user could not be added to the team")

        return redirect(self.user_teams)

class RemoveTeammate(TemplateView):
    user_teams = USER_TEAMS
    
    def post(self, request):
        try:
            # Get a player to be added
            player = RegisteredUser.objects.get(id=int(request.POST["player_id"]))
        except:
            messages.info(request, "A user does not exist")
            player = None
        
        try:
            # Get a user's team (has to be an owner)
            team = Team.objects.get(id=int(request.POST["team_id"]))

            if(team.owner.id != request.session.get("user")["id"] and int(request.POST["player_id"]) != request.session.get("user")["id"]):
                print(team, ".")
                messages.info(request, "You are not authorized to remove this player from the team")
                team = None
        except:
            messages.info(request, "The team does not exist")
            team = None

        # Create a UserTeam object to join a player to the team
        userteam = None
        if(player and team):
            try:
                userteam = UserTeam.objects.get(user=player.id, team=team.id)
                # Team must change state to unconfirmed
                team.confirmed = 0
            except:
                userteam = None
        else:
            messages.info(request, "The user is not in this team")
        
        if(userteam):
            if(team.owner.id == int(request.POST["player_id"])):
                messages.info(request, "Cannot remove the owner of the team")
            else:
                try:
                    userteam.delete()
                    team.save()
                    messages.info(request, "The user was removed from the team")
                except:
                    messages.info(request, "The user removal failed")
                    
        return redirect(self.user_teams)

class CreateTeam(TemplateView):
    user_teams = USER_TEAMS
    
    def post(self, request):
        # Prepare a blank new team
        try:
            default_name = request.session.get("user")["first_name"] + "'s Team"
            team_owner = RegisteredUser.objects.get(id=request.session.get("user")["id"])

            new_team = Team(name=default_name, owner=team_owner, tournament=None)
        except:
            new_team = None
            messages.info(request, "New team creation failed")

        # The team must have at least one player (an owner)
        if(new_team):
            try:
                # The team must be in database to be able to connect a UserTeam object
                new_team.save()

                player_owner = RegisteredUser.objects.get(id=request.session.get("user")["id"])
            except:
                player_owner = None

            # Create a UserTeam object to join a player to the team
            userteam = None
            if(player_owner):
                try:
                    userteam = UserTeam(user=player_owner, team=new_team)
                except:
                    userteam = None
            
            if(userteam):
                userteam.save()
                messages.info(request, "New team was created")
            else:
                new_team.delete()
                messages.info(request, "New team creation failed")

        return redirect(self.user_teams)

class DeleteTeam(TemplateView):
    user_teams = USER_TEAMS
    
    def post(self, request):
        try:
            team = Team.objects.get(id=int(request.POST["team_id"]))
        except:
            team = None
            messages.info(request, "The selected team does not exist")
        
        if(team):
            team.delete()
            messages.info(request, "The team was deleted")

        return redirect(self.user_teams)

class UnjoinEvent(TemplateView):
    user_teams = USER_TEAMS
    
    def post(self, request):
        # The team must be in the tournament and the user has to be its owner
        try:
            team = Team.objects.get(id=int(request.POST["team_id"]))
        except:
            messages.info(request, "The team does not exist")

        if(team):
            if(team.owner.id == request.session.get("user")["id"]):
                team.tournament = None
                team.save()

                messages.info(request, "The team successfully unjoined the tournament")
            else:
                messages.info(request, "You are not an owner of this team")

        return redirect(self.user_teams)

class FormerTeams(TemplateView):
    template_name = Teams.template_name
    user_teams = USER_TEAMS

    def get(self, request):
        former_teams = []
        try:
            # Get team IDs where a user is 
            team_ids = list(UserTeam.objects.filter(user=request.session.get("user")["id"]).values_list("team", flat=True))
            # Event ids which are Ongoing or Finished, so the teams in cannot be changed
            event_ids = list(Tournament.objects.filter(state__in=[2,3]).values_list("id", flat=True))
            # Get the teams which are in an ongoing or finished tournament
            former_db_teams = Team.objects.filter(id__in=team_ids).filter(tournament__in=event_ids)
        except:
            former_db_teams = None

        # Get the dictionary list-models with teams and members
        former_teams = Teams.get_team_list(self, former_db_teams)

        args = {
            "former_teams": former_teams,
            "showing_former": 1
        }

        return render(request, self.template_name, args)