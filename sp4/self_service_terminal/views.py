from django.shortcuts import render, HttpResponse
from .models import Form

def index(request):
    """Return the bare base.html."""
    return render(request, 'self_service_terminal/base.html')

""" TODO If entry with primary key menu_id or form_id does not exist
in the database then return the homepage."""

def menu(request, menu_id=None, menu_title=None):
    """TODO Return the menu with the primary key <menu_id>.
    
    Parameters:
    - id_homepage
    - id_parent_menu
    - submenus : {
        menu1_id : {
            menu1_name : 'somename',
            menu1_id   : 101010
        },
        ...
    }
    - number_of_submenus
    """
    context = {
        'id_homepage'       : 12345,
        'id_parent_menu'    : 54321,
        'submenus'          : {
            10101 : {
                'name'  : 'Ich bin ein Menü.',
                'id'    : 10101
            }
        }
    }
    context['number_of_submenus'] = len(context['submenus'])
    return render(request, 'self_service_terminal/menu.html', context)

def formular(request, form_id=None, form_title=None):
    """TODO Return the form with the primary key <form_id>.
    
    Parameters:
    - id_homepage
    - id_parent
    - number_of_copies
    """
    context = {
        'id_homepage'       : 1234,
        'id_parent'         : 54321,
        'number_of_copies'  : 100000000
    }
    return render(request, 'self_service_terminal/formular.html')

def print_formular(request, form_id=None):
    """TODO Just run the print function of the given form 
    and do not change the current page"""
    # Form.objects.get('id=').print_form()
    return render(request, 'self_service_terminal/formular.html')

# Testview für die Django Templatesprache

def menu_template_test(request, menu_id=None, menu_title=None):
    context = {
        'miep' : 'Was?!',
        'range': list(range(10))
    }
    return render(request, 'self_service_terminal/dtl_test.html', context)