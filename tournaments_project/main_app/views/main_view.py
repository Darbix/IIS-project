from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpResponse
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

def add_user(request):
    template = loader.get_template('main_app/add_user.html')
    return HttpResponse(template.render({}, request))

def add_user_post(request):
    n = request.POST["name"]
    user = RegisteredUser(firstname=n)
    user.save()
    return HttpResponseRedirect(reverse('index'))


def delete_user(request):
    template = loader.get_template('main_app/delete_user.html')
    return HttpResponse(template.render({}, request))

def delete_user_post(request):
    n = request.POST["name"]
    user = RegisteredUser.objects.filter(name=n)
    user.delete()
    return HttpResponseRedirect(reverse('index'))
