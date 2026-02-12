from django.http import HttpResponse


def index(request):
    return HttpResponse("Inventory app is ready.")
