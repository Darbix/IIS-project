from django.db import models

class RegisteredUser(models.Model):
    firstname = models.CharField(max_length=64)
    lastname = models.CharField(max_length=64)
    email = models.CharField(max_length=64, unique=True)
    password = models.CharField(max_length=60)
    avatar = models.ImageField(upload_to='media', default='media/default.png')
    description = models.TextField(blank=True)

# Pouze administrátor může vytvářet typy turnajů, které je možné hrát.
# Z těchto typů si následně správce turnajů můžou vybírat
class TournamentType(models.Model):
    type = models.CharField(max_length=64)

class Tournament(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(default='')
    date = models.DateField()
    prize = models.CharField(max_length=64)

    type = models.ForeignKey(TournamentType, on_delete=models.CASCADE)
    state = models.PositiveSmallIntegerField(
        choices=(
            (1, 'Created'),
            (2, 'Ongoing'),
            (3, 'Finished')
        )
    )
    minimumTeamSize = models.PositiveIntegerField()
    maximumTeamSize = models.PositiveIntegerField()

# Ukládání správců turnaje. Uživatel může spravovat více turnajů a turnaj může mít více správců
class UserTournamentModerator(models.Model):
    user = models.ForeignKey(RegisteredUser, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)


class Team(models.Model):
    name = models.CharField(max_length=64)
    owner = models.ForeignKey(RegisteredUser, on_delete=models.CASCADE)

# Ukládání týmů. Uživatel může být ve více týmech zároveň a týmy mají několik uživatelů
class UserTeam(models.Model):
    user = models.ForeignKey(RegisteredUser, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    #class Meta:
    #    unique_together = (user, team)

# Požadavek zaslaný správcem týmu uživateli o přidání do týmu
# - ať správce týmu nemůže přidávat jakékoliv uživatele
class UserTeamRequest(models.Model):
    user = models.ForeignKey(RegisteredUser, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
