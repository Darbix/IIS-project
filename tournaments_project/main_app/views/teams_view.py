from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.conf import settings

from ..models import RegisteredUser

class Teams(TemplateView):
    template_name = 'main_app/user_teams.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        return render(request, self.template_name)
