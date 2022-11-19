from django.views.generic import TemplateView
from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect

from ..models import RegisteredUser

class LoginUser(TemplateView):
    index_page = 'index'
    profile_page = 'user_profile'
    template_name = 'main_app/login_user.html'

    def get(self, request):
        user = request.session.get('user')
        if user:
            return redirect(self.profile_page)
        
        return render(request, self.template_name)
    
    def post(self, request):
        if "email" not in request.POST or "password" not in request.POST:
            # Chybějící email/heslo v post requestu - pravděpodobně někdo
            # zkouší zasílat requesty bez našeho frontendu, redirect na index
            return redirect(self.index_page)
        
        try:
            user = RegisteredUser.objects.get(email=request.POST["email"])
        except RegisteredUser.DoesNotExist as e:
            # TODO: Error hláška - uživatel s tímto emailem neexistuje
            return redirect(self.index_page)

        passwordOk = check_password(request.POST["password"], user.password)
        if not passwordOk:
            # TODO: Error hláška - špatně zadané heslo
            return redirect(self.index_page)
        
        request.session['user'] = {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'description': user.description,
            'birth_date': user.birth_date.strftime("%Y-%m-%d"),
            'avatar_url': user.avatar.url,
            'join_date': user.join_date.strftime("%Y-%m-%d"),
        }

        return redirect(self.index_page)
