from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.db.models import DateField, DateTimeField
from django.apps import apps
from django.core import serializers
from django.db.models.fields.related import ForeignKey

from main_app import models as user_models
from ..models import RegisteredAdmin

from datetime import datetime

class QueryTable(TemplateView):
    login_page = 'login'
    template_name = 'admin_app/query.html'

    # Obsahuje tuple(název_tabulky, [ názvy headeru tabulky ])
    table_names = {
        "{}".format(x.__name__) : [ "{}".format(y.name) for y in x._meta.fields ] for x in apps.get_app_config('main_app').get_models()
        if x.__name__ not in [ 'Permission', 'Group', 'User', 'ContentType', 'Session' ] # Výchozí django tabulky
    }

    def get(self, request, error_msg = None):
        if not RegisteredAdmin.IsLoggedIn(request):
            return redirect(self.login_page)
        args = {
            "table_names": self.table_names,
            "error": error_msg
        }
        return render(request, self.template_name, args)

    def post(self, request):
        if not RegisteredAdmin.IsLoggedIn(request):
            return redirect(self.login_page)

        if 'update' in request.POST:
            return self.post_update(request)
        elif 'add' in request.POST:
            return self.post_add(request)
        elif 'delete' in request.POST:
            return self.post_delete(request)
        elif 'table' in request.POST and 'sort_by' in request.POST:
            return self.post_query(request)
        return redirect('query')

    def post_query(self, request):
        table = request.POST['table']
        sortBy = request.POST['sort_by']

        try:
            model = apps.get_model('main_app', table)
        except Exception as e:
            return self.get(request, e)

        tableData = serializers.serialize("python", model.objects.all().order_by(sortBy))

        args = {
            "table_names": self.table_names,
            "table": table,
            "table_data": tableData
        }

        return render(request, self.template_name, args)

    def post_update(self, request):
        if 'table' not in request.POST or 'id' not in request.POST or 'sort_by' not in request.POST:
            # Chybí položka - nemělo by nastat
            return redirect('query')
        
        table = request.POST['table']
        id = request.POST['id']

        try:
            model = apps.get_model('main_app', table)
            instance = model.objects.get(id=id)
        except Exception as e:
            # Neexistující tabulka/id - nemělo by nastat
            return self.get(request, e)
        
        for field in model._meta.local_fields:
            if field.name in request.POST:
                try:
                    SetAttrBasedOnType(instance, field, request.POST[field.name])
                except Exception as e:
                    return self.get(request, e)
        instance.save()
        return self.post_query(request)

    def post_add(self, request):
        if 'table' not in request.POST:
            # Chybí položka - nemělo by nastat
            return redirect('query')
        table = request.POST['table']

        try:
            model = apps.get_model('main_app', table)
            instance = model()
        except Exception as e:
            # Neexistující tabulka/id - nemělo by nastat
            return self.get(request, e)

        for field in model._meta.local_fields:
            if field.name in request.POST and request.POST[field.name] != '':
                try:
                    SetAttrBasedOnType(instance, field, request.POST[field.name])
                except Exception as e:
                    return self.get(request, e)
        instance.save()
        return self.post_query(request)

    def post_delete(self, request):
        if 'table' not in request.POST or 'id' not in request.POST:
            # Chybí položka - nemělo by nastat
            return redirect('query')
        table = request.POST['table']
        id = request.POST['id']

        try:
            model = apps.get_model('main_app', table)
            instance = model.objects.get(id=id)
        except Exception as e:
            # Neexistující tabulka/id - nemělo by nastat
            return self.get(request, e)
        instance.delete()
        return self.post_query(request)

# Nastaví atribut zadané instanci dle typu hodnoty
def SetAttrBasedOnType(instance, field, value):
    if type(field) == DateTimeField:
        setattr(instance, field.name, datetime.strptime(value, "%Y-%m-%d %H-%M-%S"))
    elif type(field) == DateField:
        setattr(instance, field.name, datetime.strptime(value, "%Y-%m-%d"))
    elif type(field) == ForeignKey:
        setattr(instance, field.name + "_id", value)
    else:
        setattr(instance, field.name, value)