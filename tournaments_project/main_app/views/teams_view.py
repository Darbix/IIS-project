from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.conf import settings
from itertools import chain
from django.db.models import Q
from django.contrib import messages
from ..models import RegisteredUser, Team, UserTeam, Tournament

USER_TEAMS = "user_teams"

class Teams(TemplateView):
    template_name = 'main_app/user_teams.html'

    def get(self, request):
        # TODO old teams

        try:
            # All the teams a user owns
            created_teams = Team.objects.filter(owner=request.session.get("user")["id"])

        except:
            created_teams = None
        
        try:
            # All the teams (ids) containing a user
            team_ids = list(UserTeam.objects.filter(user=request.session.get("user")["id"]).values_list("team", flat=True))

            # Get all teams a user is present in except those where the user is an owner 
            teams_with_user = Team.objects.filter(id__in=team_ids).filter(~Q(owner=request.session.get("user")["id"]))
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

    def post(self, request):
        return render(request, self.template_name)


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
        if(team and player):
            try:
                userteam = UserTeam(user=player, team=team)
            except:
                userteam = None
        
        if(userteam):
            userteam.save()
            messages.info(request, "The user was added to your team")

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
            except:
                userteam = None
        else:
            messages.info(request, "The user is not in this team")
        
        if(userteam):
            userteam.delete()
            messages.info(request, "The user was removed from the team")

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
        print(request.POST)

        return redirect(self.user_teams)