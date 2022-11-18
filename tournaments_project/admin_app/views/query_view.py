from django.views.generic import TemplateView
from django.shortcuts import render, redirect

from ..models import RegisteredAdmin

import django.apps

from django.apps import apps
from django.core import serializers

class QueryTable(TemplateView):
    login_page = 'login'
    template_name = 'admin_app/query.html'

    # Obsahuje tuple(název_tabulky, [ názvy headeru tabulky ])
    table_names = [
        ("{}".format(x.__name__), [ "{}".format(y.name) for y in x._meta.fields ]) for x in django.apps.apps.get_models()
        if x.__name__ not in [ 'Permission', 'Group', 'User', 'ContentType', 'Session' ] # Výchozí django tabulky
    ]

    def get(self, request):
        if not RegisteredAdmin.IsLoggedIn(request):
            return redirect(self.login_page)
        print(self.table_names)
        args = {
            "table_names": self.table_names
        }
        return render(request, self.template_name, args)

    def post(self, request):
        if not RegisteredAdmin.IsLoggedIn(request):
            return redirect(self.login_page)
        table = request.POST.get('table')
        sortBy = request.POST.get('sort_by')

        if not table or not sortBy:
            # Nemělo by nastat!
            return redirect('query')

        try:
            model = apps.get_model(app_label='main_app', model_name=table)
        except:
            return redirect('query')

        tableData = serializers.serialize("python", model.objects.all().order_by(sortBy))
        print(tableData)

        args = {
            "table_names": self.table_names,
            "table": table,
            "table_data": tableData
        }

        return render(request, self.template_name, args)