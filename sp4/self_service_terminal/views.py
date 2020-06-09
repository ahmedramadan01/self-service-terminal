from django.core.paginator import Paginator
from django.shortcuts import render, HttpResponse
from .models import Menu, Form, Terminal_Settings

from pdf2image import convert_from_path
import os

# TEMP: Define the settings as the first entry of all Terminal_Settings
# settings = list(Terminal_Settings.objects.all())[0]
def get_settings():
    return list(Terminal_Settings.objects.all())[0]

def index(request):
    settings = get_settings()

    homepage_id = list(Terminal_Settings.objects.all())[0].homepage_id
    homepage = Menu.objects.get(pk=homepage_id)

    submenus = list(Menu.objects.filter(parent_menu=homepage_id))
    subforms = list(Form.objects.filter(parent_menu=homepage_id))

    context = {
        'settings': settings,
        'menu': homepage,
        'submenus': submenus,
        'subforms': subforms
    }
    return render(request, 'self_service_terminal/menu.html', context)


def menu(request, menu_id=None, menu_title=None):
    """Return the menu site with the primary key <menu_id>.
    """
    settings = get_settings()

    menu = Menu.objects.get(pk=menu_id)
    submenus = list(Menu.objects.filter(parent_menu=menu_id))
    subforms = list(Form.objects.filter(parent_menu=menu_id))

    # Fill the paginator with all submenus and subforms
    paginator = Paginator(submenus + subforms, 5)

    # Get the current page from the HTTP Request
    page_number = request.GET.get('page')

    # Get all objects that are allowed on the current page
    page_obj = paginator.get_page(page_number)

    # Add option to test for Menu and Form object
    for i in range(len(page_obj.object_list)):
        page_obj.object_list[i] = {
            'object': page_obj.object_list[i],
            'is_menu': type(page_obj.object_list[i]) is Menu,
            'is_form': type(page_obj.object_list[i]) is Form
        }

    context = {
        'settings': settings,
        'menu': menu,
        'page_obj': page_obj
    }
    return render(request, 'self_service_terminal/menu.html', context)


def formular(request, form_id=None, form_title=None):
    """Return the form site with the primary key <form_id>.
    """
    settings = get_settings()

    form = Form.objects.get(pk=form_id)

    # Convert first page of pdffile to jpg and save it
    try:
        path = form.pdffile.path
        folder = path.rsplit('/', maxsplit=1)[0]
        img_path = form.pdffile.path.split('.')[0]
        if not os.path.isfile(img_path):
            convert_from_path(
                form.pdffile.path,
                output_folder=folder,
                first_page=1,
                last_page=1,
                fmt='jpeg',
                single_file=True,
                output_file=img_path
            )
        img_url = form.pdffile.url.rsplit('.', maxsplit=1)[0] + '.jpg'
    except Exception:
        img_url = settings.krankenkasse_logo.url

    parent_page_number = request.GET.get('page')

    context = {
        'settings': settings,
        'form': form,
        'img_path': img_url,
        'parent_page_number': parent_page_number
    }
    return render(request, 'self_service_terminal/formular.html', context)


def print_formular(request, form_id=None):
    """Run the print method of the given form object
    and return a HTTP 204 No Content response."""
    Form.objects.get(pk=form_id).print_form()
    return HttpResponse(status=204)


# Testview für die Django Templatesprache
def menu_template_test(request, menu_id=None, menu_title=None):
    settings = get_settings()
    if menu_id:
        menu = Menu.objects.get(pk=menu_id)
        submenus = list(Menu.objects.filter(parent_menu=menu_id))
        subforms = list(Form.objects.filter(parent_menu=menu_id))
        
        # Fill the paginator with all submenus and subforms
        paginator = Paginator(submenus + subforms, 5)

        # Get the current page from the HTTP Request
        page_number = request.GET.get('page')
        # Get all objects that are allowed on the current page
        page_obj = paginator.get_page(page_number)

        # Add option to test for Menu and Form object
        for i in range(len(page_obj.object_list)):
            page_obj.object_list[i] = {
                'object': page_obj.object_list[i],
                'is_menu': type(page_obj.object_list[i]) is Menu,
                'is_form': type(page_obj.object_list[i]) is Form
            }
        
        # Only for debugging purposes
        # print(page_obj.object_list)

        context = {
            'settings': settings,
            'menu': menu,
            'page_obj': page_obj
        }
        return render(request, 'self_service_terminal/dtl_test.html', context)

    else:
        homepage_id = list(Terminal_Settings.objects.all())[0].homepage_id
        homepage = Menu.objects.get(pk=homepage_id)

        submenus = list(Menu.objects.filter(parent_menu=homepage_id))
        subforms = list(Form.objects.filter(parent_menu=homepage_id))

        paginator = Paginator(submenus + subforms, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        for i in range(len(page_obj.object_list)):
            page_obj.object_list[i] = {
                'object': page_obj.object_list[i],
                'is_menu': type(page_obj.object_list[i]) is Menu,
                'is_form': type(page_obj.object_list[i]) is Form
            }

        context = {
            'settings': settings,
            'menu': homepage,
            'page_obj': page_obj
        }
        return render(request, 'self_service_terminal/dtl_test.html', context)
