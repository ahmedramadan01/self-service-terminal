from django.shortcuts import render, HttpResponse

def index(request):
    """Return the homepage."""
    return render(request, 'self_service_terminal/index.html')

""" TODO If entry with primary key menuid or formid does not exist
in the database then return the homepage."""

def menu(request, menu_id=None, menu_title=None):
    """TODO Return the menu with the primary key <menuid>."""
    return render(request, 'self_service_terminal/years.html') 

def formular(request, form_id=None, form_title=None):
    """TODO Return the form with the primary key <formid>."""
    return render(request, 'self_service_terminal/formular.html')

# Testview für die Django Templatesprache

def menu_template_test(request, menu_id=None, menu_title=None):
    context = {
        'miep' : 'Was?!',
        'range': list(range(10))
    }
    return render(request, 'self_service_terminal/dtl_test.html', context)