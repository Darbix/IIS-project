from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

from ..models import RegisteredUser

# Create your views here.
def index(request):
    users = list(RegisteredUser.objects.all().values())
    args = {
        "users": users,
        "user": None} # TODO test logged out user
    return HttpResponse(loader.get_template('main_app/index.html').render(args, request))


# TODO Temp renders
def register_todo(request):
   return HttpResponse(loader.get_template('main_app/register_user.html').render(None, request))
def profile_todo(request):
   return HttpResponse(loader.get_template('main_app/user_profile.html').render(None, request))