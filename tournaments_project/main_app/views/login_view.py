from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView
from django.contrib.auth.hashers import check_password
from django.shortcuts import render

from ..models import RegisteredUser

class LoginUser(TemplateView):
    index_template_name = 'main_app/login_user.html'
    template_name = 'main_app/login_user.html'

    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        if "email" not in request.POST or "password" not in request.POST:
            # TODO: Error hláška - chybějící email/heslo v post requestu
            return render(request, self.index_template_name)
        try:
            user = RegisteredUser.objects.get(email=request.POST["email"])
        except RegisteredUser.DoesNotExist as e:
            # TODO: Error hláška - uživatel s tímto emailem neexistuje
            return render(request, self.index_template_name)

        passwordOk = check_password(request.POST["password"], user.password)
        if not passwordOk:
            # TODO: Error hláška - špatně zadané heslo
            return render(request, self.index_template_name)
        request.session['member_id'] = user.id
        return render(request, self.index_template_name)

