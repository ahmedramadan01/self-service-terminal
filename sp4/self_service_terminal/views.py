from django.shortcuts import render, HttpResponse
from .models import Menu, Form, Terminal_Settings


def index(request):
    homepage_id = list(Terminal_Settings.objects.all())[0].homepage_id
    homepage = Menu.objects.get(pk=homepage_id)
    submenus = list(Menu.objects.filter(parent_menu=homepage_id))
    subforms = list(Form.objects.filter(parent_menu=homepage_id))
    context = {
        'menu': homepage,
        'submenus': submenus,
        'subforms': subforms
    }
    return render(request, 'self_service_terminal/menu.html', context)


""" TODO If entry with primary key menu_id or form_id does not exist
in the database then return the homepage."""


def menu(request, menu_id=None, menu_title=None):
    """Return the menu with the primary key <menu_id>.

    Parameters:
    - menu object
    - list of submenu objects
    - list of subforms objects
    """
    menu = Menu.objects.get(pk=menu_id)
    submenus = list(Menu.objects.filter(parent_menu=menu_id))
    subforms = list(Form.objects.filter(parent_menu=menu_id))
    context = {
        'menu': menu,
        'submenus': submenus,
        'subforms': subforms
    }
    return render(request, 'self_service_terminal/menu.html', context)


def formular(request, form_id=None, form_title=None):
    """Return the form with the primary key <form_id>.

    Parameters:
    - form object
    """
    form = Form.objects.get(pk=form_id)
    context = {
        'form': form
    }
    return render(request, 'self_service_terminal/formular.html', context)


def print_formular(request, form_id=None):
    """Run the print method of the given form object
    and return a HTTP 204 No Content response."""
    Form.objects.get(pk=form_id).print_form()
    return HttpResponse(status=204)


# Testview für die Django Templatesprache
def menu_template_test(request, menu_id=None, menu_title=None):
    menu = Menu.objects.get(pk=menu_id)
    submenus = list(Menu.objects.filter(parent_menu=menu_id))
    subforms = list(Form.objects.filter(parent_menu=menu_id))
    context = {
        'menu': menu,
        'submenus': submenus,
        'subforms': subforms,
        'miep': 'Was?!',
        'range': list(range(10))
    }
    return render(request, 'self_service_terminal/dtl_test.html', context)
