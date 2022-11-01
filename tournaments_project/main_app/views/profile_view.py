from pathlib import Path
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password, make_password
from django.conf import settings

from ..models import RegisteredUser

from PIL import Image


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
            print("ouch")
            return redirect(self.login_user_page)
        
        try:
            user = RegisteredUser.objects.get(id=session_user['id'])
        except RegisteredUser.DoesNotExist as _:
            # Error - uživatel s tímto id neexistuje, asi byl smazán adminem, smažeme session cookie
            print("2ouch")
            del request.session['user']
            return redirect(self.index_page)

        if "first_name" in request.POST:
            user.first_name = request.POST["first_name"]
            print("1")
        if "last_name" in request.POST:
            user.last_name = request.POST["last_name"]
            print("2")
        if "description" in request.POST:
            user.description = request.POST["description"]
            print("3")
        if "birth_date" in request.POST:
            user.birth_date = request.POST["birth_date"]
        if "old_password" in request.POST and "new_password" in request.POST:
            passwordOk = check_password(request.POST["old_password"], user.password)
            if passwordOk:
                encryptedPassword = make_password(request.POST["new_password"])
                user.password = encryptedPassword
        user.save()
        
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

        file_path = "/avatars/" + str(user.id) + ".png"
        new_path = settings.MEDIA_ROOT + file_path
        try:
            im = Image.open(file)
            im.resize((256, 256))
            im.save(Path(new_path), "PNG")
        except Exception as e:
            # Neplatný img soubor
            return redirect(self.index_page)
        user.avatar = file_path
        user.save()

        # update session
        request.session['user']['avatar_url'] = user.avatar.url

        response = redirect(self.profile_page)
        response['only-if-cached'] = 'must-revalidate' # (!) Jinak se avatary neupdatují
        return response