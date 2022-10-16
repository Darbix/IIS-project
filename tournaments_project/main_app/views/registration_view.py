from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError
from django.views.generic import TemplateView
from django.shortcuts import render

from ..models import RegisteredUser

class AddUser(TemplateView):
    index_template_name = 'main_app/login_user.html'
    template_name = 'main_app/add_user.html'

    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        if "first_name" not in request.POST or "last_name" not in request.POST\
        or "email" not in request.POST or "password" not in request.POST:
            # TODO: Error hláška - chybějící argument
            return render(request, self.template_name)
        
        encryptedPassword = make_password(request.POST["password"])
        user = RegisteredUser(
            first_name=request.POST["first_name"],
            last_name=request.POST["last_name"],
            email=request.POST["email"],
            password=encryptedPassword
        )
        try:
            user.save()
        except IntegrityError as e:
            # TODO: Error hláška - email je již používán
            pass

        return render(request, self.index_template_name)