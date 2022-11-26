from django.contrib.auth.hashers import make_password
from django.db import IntegrityError
from django.views.generic import TemplateView
from django.shortcuts import render, redirect

from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from ..models import RegisteredUser

class AddUser(TemplateView):
    template_name = 'main_app/register_user.html'
    login_page = 'login_user'

    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        if "first_name" not in request.POST or "last_name" not in request.POST\
        or "email" not in request.POST or "password" not in request.POST:
            # TODO: Error hláška - chybějící argument
            return render(request, self.template_name)

        try:
            validate_email(request.POST["email"])
        except ValidationError as _:
            # TODO: Error hláška - nevalidní email
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
        return redirect(self.login_page)