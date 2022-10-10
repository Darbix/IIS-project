from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpResponse
from django.template import loader
from django.urls import reverse
from ..models import User

def login_user(request):
    template = loader.get_template('login_user.html')
    args = {
        "user": "ok"} # TODO test logged in user
    return HttpResponse(template.render(args, request))