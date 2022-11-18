from django.views.generic import TemplateView
from django.shortcuts import redirect

class LogoutAdmin(TemplateView):
    login_page = 'admin_app/login.html'

    def get(self, request):
        admin = request.session.get('admin')
        if admin:
            del request.session['admin']
        return redirect(self.login_page)
