from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.views.generic import TemplateView

from django.shortcuts import render, redirect

from admin_app import models as admin_models
from main_app import models as user_models

class MainAdmin(TemplateView):
    def get(self, request):
        users = list(user_models.RegisteredUser.objects.all().values().order_by("id"))
        admins = list(admin_models.RegisteredAdmin.objects.all().values().order_by("id"))

        args = {
            "users": users,
            "admins": admins,
        }
        return HttpResponse(loader.get_template('admin_app/index.html').render(args, request))

    def post(self, request):
        user_id = request.POST["id"]
        user = user_models.RegisteredUser.objects.get(id=user_id)
        user.first_name = "Honza"
        user.save()

        return HttpResponseRedirect("/admin/")