from django.shortcuts import render
from .models import User

# Create your views here.
def index(request):
    users = list(User.objects.all().values())

    args = {"users": users}

    return render(request, 'index.html', args)