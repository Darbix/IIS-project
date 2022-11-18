from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.hashers import check_password

from ..models import RegisteredAdmin

class LoginAdmin(TemplateView):
    template_name = 'admin_app/login.html'
    index_page = '/admin/'

    def get(self, request):
        # RegisteredAdmin.CreateDefaultAdmin()
        if RegisteredAdmin.IsLoggedIn(request):
            return redirect(self.index_page)
        
        return render(request, self.template_name)

    def post(self, request):
        if "email" not in request.POST or "password" not in request.POST:
            # TODO: Error hláška - chybějící email/heslo v post requestu
            return render(request, self.template_name)
        try:
            admin = RegisteredAdmin.objects.get(email=request.POST["email"])
        except RegisteredAdmin.DoesNotExist as e:
            # TODO: Error hláška - uživatel s tímto emailem neexistuje
            return render(request, self.template_name)

        passwordOk = check_password(request.POST["password"], admin.password)
        if not passwordOk:
            # TODO: Error hláška - špatně zadané heslo
            return render(request, self.template_name)
        request.session['admin'] = {
            'id': admin.id,
            'first_name': admin.first_name,
            'last_name': admin.last_name
        }
        return redirect(self.index_page)
