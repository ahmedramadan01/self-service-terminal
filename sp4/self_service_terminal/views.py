from django.shortcuts import render, HttpResponse

def index(request):
    return render(request, 'self_service_terminal/index.html')

def years(request):
    return render(request, 'self_service_terminal/years.html')    

def formular(request):
    return render(request, 'self_service_terminal/formular.html')