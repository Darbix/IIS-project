from django.views.generic import TemplateView
from django.shortcuts import redirect

class LogoutUser(TemplateView):
    index_page = 'index'

    def get(self, request):
        # smažeme session id a redirectneme na index stránku
        user = request.session.get('user')
        if user:
            del request.session['user']
        return redirect(self.index_page)
