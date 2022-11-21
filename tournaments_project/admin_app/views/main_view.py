from django.views.generic import TemplateView
from django.shortcuts import render, redirect

from ..models import RegisteredAdmin

from main_app import models as user_models

class MainAdmin(TemplateView):
    template_name = 'admin_app/index.html'
    login_page = 'login'

    def get(self, request):
        if not RegisteredAdmin.IsLoggedIn(request):
            return redirect(self.login_page)

        user_count = user_models.RegisteredUser.objects.all().count()
        tournaments = user_models.Tournament.objects.all()
        tournament_types = user_models.TournamentType.objects.all()
        tournaments_count = [ 0, 0, 0, 0 ]

        for tournament in tournaments:
            tournaments_count[tournament.state] += 1

        args = {
            "user_count": user_count,
            "tournaments_count": tournaments_count,
            "tournament_types": tournament_types.count(),
        }
        return render(request, self.template_name, args)