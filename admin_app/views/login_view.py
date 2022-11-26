from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.hashers import check_password

from ..models import RegisteredAdmin

class LoginAdmin(TemplateView):
    template_name = 'admin_app/login.html'
    index_page = '/admin/'

    def get(self, request):
        if RegisteredAdmin.IsLoggedIn(request):
            return redirect(self.index_page)
        
        return render(request, self.template_name)

    def post(self, request):
        if "email" not in request.POST or "password" not in request.POST:
            return render(request, self.template_name, {"error": "Missing email and/or password"})
        try:
            admin = RegisteredAdmin.objects.get(email=request.POST["email"])
        except RegisteredAdmin.DoesNotExist as e:
            return render(request, self.template_name, {"error": "User with this email doesn't exist"})

        passwordOk = check_password(request.POST["password"], admin.password)
        if not passwordOk:
            return render(request, self.template_name, {"error": "Incorrect password"})

        request.session['admin'] = {
            'id': admin.id,
            'first_name': admin.first_name,
            'last_name': admin.last_name
        }
        return redirect(self.index_page)
