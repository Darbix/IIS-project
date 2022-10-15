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

def delete_user(request):
    template = loader.get_template('main_app/delete_user.html')
    return HttpResponse(template.render({}, request))

def delete_user_post(request):
    n = request.POST["name"]
    user = RegisteredUser.objects.filter(name=n)
    user.delete()
    return HttpResponseRedirect(reverse('index'))
