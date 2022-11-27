from django.db import models
import datetime

class RegisteredUser(models.Model):
    # Vyžadované
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    email = models.CharField(max_length=64, unique=True)
    password = models.CharField(max_length=88)
    # Nastavitelné po registraci
    birth_date = models.DateField(default=datetime.datetime(1970, 1, 1))
    avatar = models.ImageField(upload_to='/media/avatars/', default='/media/avatars/default.png')
    description = models.TextField(blank=True)
    join_date = models.DateField(default=datetime.date.today)

# Pouze administrátor může vytvářet typy turnajů, které je možné hrát.
# Z těchto typů si následně správce turnajů můžou vybírat
class TournamentType(models.Model):
    type = models.CharField(max_length=64)

class Tournament(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(default='')
    date = models.DateTimeField()
    prize = models.CharField(max_length=64)
    capacity = models.PositiveIntegerField(blank=False)

    type = models.ForeignKey(TournamentType, on_delete=models.CASCADE)
    state = models.PositiveSmallIntegerField(
        choices=(
            (0, 'Unconfirmed'),
            (1, 'Confirmed'),
            (2, 'Ongoing'),
            (3, 'Finished')
        )
    )
    minimum_team_size = models.PositiveIntegerField()
    maximum_team_size = models.PositiveIntegerField()

# Ukládání správců turnaje. Uživatel může spravovat více turnajů a turnaj může mít více správců
class UserTournamentModerator(models.Model):
    user = models.ForeignKey(RegisteredUser, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)

class Team(models.Model):
    name = models.CharField(max_length=64)
    owner = models.ForeignKey(RegisteredUser, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, null=True)
    confirmed = models.PositiveSmallIntegerField(
        choices=(
            (0, 'Unconfirmed'),
            (1, 'Confirmed')
        ), default=0
    )
    avatar = models.ImageField(upload_to='/media/avatars/', default='/media/avatars/default.png')

# Ukládání týmů. Uživatel může být ve více týmech zároveň a týmy mají několik uživatelů
class UserTeam(models.Model):
    user = models.ForeignKey(RegisteredUser, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('user', 'team')

class TournamentMatch(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    state = models.PositiveSmallIntegerField(
        choices=(
            (1, 'Not started'),
            (2, 'Ongoing'),
            (3, 'Finished')
        )
    )
    team_1_score = models.PositiveIntegerField()
    team_2_score = models.PositiveIntegerField()

class TournamentRound(models.Model):
    match = models.ForeignKey(TournamentMatch, on_delete=models.CASCADE)
    team_1 = models.ForeignKey(Team, null=True, on_delete=models.SET_NULL, related_name='%(class)s_team_1')
    team_2 = models.ForeignKey(Team, null=True, on_delete=models.SET_NULL, related_name='%(class)s_team_2')

class KnockoutMatch(models.Model):
    match = models.ForeignKey(TournamentMatch, on_delete=models.CASCADE)
    team_1_match_winner = models.ForeignKey(TournamentMatch, on_delete=models.CASCADE, related_name='%(class)s_team_1_match_winner')
    team_2_match_winner = models.ForeignKey(TournamentMatch, on_delete=models.CASCADE, related_name='%(class)s_team_2_match_winner')
