from django.shortcuts import render, HttpResponse

def index(request):
    """Return the bare base.html."""
    return render(request, 'self_service_terminal/index.html')

""" TODO If entry with primary key menu_id or form_id does not exist
in the database then return the homepage."""

def menu(request, menu_id=None, menu_title=None):
    """TODO Return the menu with the primary key <menu_id>."""

    return render(request, 'self_service_terminal/menu.html') 

def formular(request, form_id=None, form_title=None):
    """TODO Return the form with the primary key <form_id>."""
    return render(request, 'self_service_terminal/formular.html')

def print_formular(request, form_id=None):
    """TODO Just run the print function of the given form 
    and do not change the current page"""
    return render(request, 'self_service_terminal/formular.html')

# Testview für die Django Templatesprache

def menu_template_test(request, menu_id=None, menu_title=None):
    context = {
        'miep' : 'Was?!',
        'range': list(range(10))
    }
    return render(request, 'self_service_terminal/dtl_test.html', context)