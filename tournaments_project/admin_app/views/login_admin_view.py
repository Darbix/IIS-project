from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.hashers import check_password

from ..models import RegisteredAdmin

# Create your views here.

class LoginAdmin(TemplateView):
    index_template_name = 'admin_app/login.html'
    template_name = 'admin_app/login.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        if "email" not in request.POST or "password" not in request.POST:
            # TODO: Error hláška - chybějící email/heslo v post requestu
            return render(request, self.index_template_name)
        try:
            admin = RegisteredAdmin.objects.get(email=request.POST["email"])
        except RegisteredAdmin.DoesNotExist as e:
            # TODO: Error hláška - uživatel s tímto emailem neexistuje
            return render(request, self.index_template_name)

        passwordOk = check_password(request.POST["password"], admin.password)
        if not passwordOk:
            # TODO: Error hláška - špatně zadané heslo
            return render(request, self.index_template_name)
        request.session['admin_id'] = admin.id
        return render(request, self.index_template_name)
