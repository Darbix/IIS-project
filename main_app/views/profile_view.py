from pathlib import Path
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password, make_password
from django.conf import settings
from django.contrib import messages

from ..models import RegisteredUser

from PIL import Image
from datetime import datetime


class Profile(TemplateView):
    login_user_page = 'login_user'
    template_name = 'main_app/user_profile.html'

    def get(self, request):
        user = request.session.get('user')
        if not user:
            return redirect(self.login_user_page)
        
        return render(request, self.template_name)

    def post(self, request):
        # Post request pro změnu údajů. Email není možné měnit - nepoužíváme
        # emailového klienta pro zaslání kontrolního mailu
        session_user = request.session.get('user')
        if not session_user:
            return redirect(self.login_user_page)
        
        try:
            user = RegisteredUser.objects.get(id=session_user['id'])
        except RegisteredUser.DoesNotExist as _:
            # Error - uživatel s tímto id neexistuje, asi byl smazán adminem, smažeme session cookie
            del request.session['user']
            return redirect(self.index_page)

        if "first_name" in request.POST:
            user.first_name = request.POST["first_name"]
        if "last_name" in request.POST:
            user.last_name = request.POST["last_name"]
        if "description" in request.POST:
            user.description = request.POST["description"]
        if "birthdate" in request.POST:
            user.birth_date = datetime.strptime(request.POST["birthdate"], "%Y-%m-%d")
        if "old_password" in request.POST and "new_password" in request.POST:
            passwordOk = check_password(request.POST["old_password"], user.password)
            if passwordOk:
                encryptedPassword = make_password(request.POST["new_password"])
                user.password = encryptedPassword
        user.save()

        # potřeba updatovat session
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
        return render(request, self.template_name)

class ProfileImageUpload(TemplateView):
    profile_page = 'user_profile'
    index_page = 'index'

    def post(self, request):
        file = request.FILES.get('avatar')
        session_user = request.session.get('user')
        if not file or not session_user:
            return redirect(self.profile_page)

        try:
            user = RegisteredUser.objects.get(id=session_user['id'])
        except RegisteredUser.DoesNotExist as _:
            # Error - uživatel s tímto id neexistuje, asi byl smazán adminem, smažeme session cookie
            del request.session['user']
            return redirect(self.index_page)

        file_path = "/static/avatars/" + str(user.id) + ".png"
        new_path = str(settings.BASE_DIR) + file_path
        try:
            im = Image.open(file)
            im.resize((256, 256))
            im.save(new_path, "PNG")
        except Exception as e:
            messages.info(request, "Invalid image")
            return redirect(self.index_page)
        user.avatar = file_path
        user.save()

        # update session - update 1 položky nelze z nějakého důvodu
        request.session['user'] = {
            'id': request.session['user']['id'],
            'first_name': request.session['user']['first_name'],
            'last_name': request.session['user']['last_name'],
            'email': request.session['user']['email'],
            'description': request.session['user']['description'],
            'birth_date': request.session['user']['birth_date'],
            'avatar_url': file_path,
            'join_date': request.session['user']['join_date'],
        }
        return redirect(self.profile_page)