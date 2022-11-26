from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password

from ..models import RegisteredAdmin

from main_app import models as user_models

class Users(TemplateView):
    template_name = 'admin_app/users.html'
    template_name_single = 'admin_app/user.html'
    login_page = 'login'
    header = [ "{}".format(x.name) for x in user_models.RegisteredUser._meta.fields ]

    def get(self, request, error_msg=None, *args, **kwargs):
        if not RegisteredAdmin.IsLoggedIn(request):
            return redirect(self.login_page)

        if 'user_id' not in kwargs:
            return self.get_all(request, error_msg)
        else:
            return self.get_single(request, kwargs['user_id'], error_msg)

    def get_single(self, request, id, error_msg=None):
        user = user_models.RegisteredUser.objects.get(id=id)
        user_teams = user_models.UserTeam.objects.filter(user=user)

        args = {
            'user': user,
            'user_teams': user_teams,
            'error': error_msg,
        }
        return render(request, self.template_name_single, args)

    def get_all(self, request, error_msg=None):
        users = user_models.RegisteredUser.objects.all()

        args = {
            "header": self.header,
            "users": users,
            'error': error_msg,
        }
        return render(request, self.template_name, args)
    
    def post(self, request, *args, **kwargs):
        if not RegisteredAdmin.IsLoggedIn(request):
            return redirect(self.login_page)
        
        if 'user_id' in kwargs:
            if 'update' in request.POST:
                return self.postUpdate(request, kwargs['user_id'])
            elif 'delete' in request.POST:
                return self.postDelete(request, kwargs['user_id'])
        return redirect('users')

    def postUpdate(self, request, id):
        try:
            user = user_models.RegisteredUser.objects.get(id=id)
        except:
            # Uživatel neexistuje - nemělo by nastat
            return redirect('users')

        for field in user_models.RegisteredUser._meta.local_fields:
            if field.name in request.POST and field.name != 'id' and field.name != 'join_date':
                if field.name == 'password':
                    setattr(user, field.name, make_password(request.POST[field.name]))
                else:
                    setattr(user, field.name, request.POST[field.name])
        try:
            user.save()
        except Exception as e:
            return self.get(request, e)
        return redirect('users')

    def postDelete(self, request, id):
        try:
            user = user_models.RegisteredUser.objects.get(id=id)
        except:
            # Uživatel neexistuje - nemělo by nastat
            return redirect('users')
        try:
            user.delete()
        except Exception as e:
            return self.get(request, e)
            
        return redirect('users')
