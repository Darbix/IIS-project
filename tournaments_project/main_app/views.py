from django.shortcuts import render
from .models import RegisteredUser

# Create your views here.
def index(request):
    args = {}
    return render(request, 'main_app/index.html', args)