from django.shortcuts import render, HttpResponse

def index(request):
    """Return the homepage."""
    return render(request, 'self_service_terminal/index.html')

def menu(request, menuid):
    """Return the menu with the primary key <menuid>."""
    return render(request, 'self_service_terminal/years.html') 

def formular(request, formid):
    """Return the form with the primary key <formid>."""
    return render(request, 'self_service_terminal/formular.html')