from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password

from ..models import RegisteredAdmin

class Admins(TemplateView):
    template_name = 'admin_app/admins.html'
    template_name_single = 'admin_app/admin.html'
    login_page = 'login'
    header = [ "{}".format(x.name) for x in RegisteredAdmin._meta.fields ]

    def get(self, request, error_msg = None, *args, **kwargs):
        if not RegisteredAdmin.IsLoggedIn(request):
            return redirect(self.login_page)

        if 'admin_id' not in kwargs:
            return self.get_all(request, error_msg)
        else:
            return self.get_single(request, kwargs['admin_id'], error_msg)

    def get_single(self, request, id, error_msg):
        admin = RegisteredAdmin.objects.get(id=id)

        args = {
            'admin': admin,
            'error': error_msg,
        }
        return render(request, self.template_name_single, args)

    def get_all(self, request, error_msg):
        admins = RegisteredAdmin.objects.all()

        args = {
            "headers": self.header,
            "admins": admins,
            'error': error_msg,
        }
        return render(request, self.template_name, args)
    
    def post(self, request, *args, **kwargs):
        if not RegisteredAdmin.IsLoggedIn(request):
            return redirect(self.login_page)
        
        if 'add' in request.POST:
            return self.postAdd(request)
        elif 'admin_id' in kwargs:
            if 'update' in request.POST:
                return self.postUpdate(request, kwargs['admin_id'])
            elif 'delete' in request.POST:
                return self.postDelete(kwargs['admin_id'])
        return redirect('admins')

    def postAdd(self, request):
        if 'first_name' not in request.POST or 'last_name' not in request.POST \
        or 'email' not in request.POST or 'password' not in request.POST:
            return redirect('admins')
        
        admin = RegisteredAdmin(
            first_name = request.POST['first_name'],
            last_name = request.POST['last_name'],
            email = request.POST['email'],
            password = make_password(request.POST['password'])
        )
        try:
            admin.save()
        except Exception as e:
            return self.get(request, e)

        return redirect('admins')

    def postUpdate(self, request, id):
        try:
            admin = RegisteredAdmin.objects.get(id=id)
        except:
            # Uživatel neexistuje - nemělo by nastat
            return redirect('admins')

        for field in RegisteredAdmin._meta.local_fields:
            if field.name in request.POST and field.name != 'id' and field.name != 'join_date':
                if field.name == 'password':
                    setattr(admin, field.name, make_password(request.POST[field.name]))
                else:
                    setattr(admin, field.name, request.POST[field.name])
        try:
            admin.save()
        except Exception as e:
            return self.get(request, e)

        return redirect('admins')

    def postDelete(self, id):
        try:
            admin = RegisteredAdmin.objects.get(id=id)
        except:
            # Uživatel neexistuje - nemělo by nastat
            return redirect('admins')
        
        admin.delete()
        return redirect('admins')
