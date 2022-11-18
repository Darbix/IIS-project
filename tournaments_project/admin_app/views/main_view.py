from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
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

        users = list(user_models.RegisteredUser.objects.all().values().order_by("id"))
        admins = list(RegisteredAdmin.objects.all().values().order_by("id"))

        args = {
            "users": users,
            "admins": admins,
        }
        return render(request, self.template_name)