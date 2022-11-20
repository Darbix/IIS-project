from django.views.generic import TemplateView
from django.shortcuts import render, redirect

from ..models import RegisteredAdmin

from main_app import models as user_models

class Tournaments(TemplateView):
    template_name = 'admin_app/tournaments.html'
    login_page = 'login'
    header = [ "{}".format(x.name) for x in user_models.Tournament._meta.fields ]

    def get(self, request):
        if not RegisteredAdmin.IsLoggedIn(request):
            return redirect(self.login_page)

        tournaments = user_models.Tournament.objects.all()

        # 2 query nebo filtrovat "ručně"?
        unconfirmed = user_models.Tournament.objects.filter(state=0)
        # unconfirmed = list([ t for t in tournaments if t.state == 0 ])

        args = {
            "header": self.header,
            "unconfirmed_tournaments": unconfirmed,
            "all_tournaments": tournaments
        }
        return render(request, self.template_name, args)