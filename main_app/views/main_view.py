from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

from ..models import RegisteredUser

# Main page load
def index(request):

    return HttpResponse(loader.get_template('main_app/index.html').render(None, request))


def handler404(request, exception):
    return HttpResponse(loader.get_template("page_not_found.html").render(None, request), status=404)
