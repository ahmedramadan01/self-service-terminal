from django.shortcuts import render, HttpResponse

def index(request):
    return render(request, 'self_service_terminal/index.html')

def years(request):
    return render(request, 'self_service_terminal/years.html')

# TODO add parameters needed to generate the view
# TODO write a template
def menu(request):
    return render(request, 'self_service_terminal/menu.html') 

def formular(request):
    return render(request, 'self_service_terminal/formular.html')