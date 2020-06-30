from django.core.paginator import Paginator
from django.shortcuts import render, HttpResponse
from django.http import HttpRequest
from self_service_terminal.models import Menu, Form, Terminal_Settings
from self_service_terminal.admin import MenuResource, FormResource, Terminal_SettingsResource

from pdf2image import convert_from_path
from datetime import datetime
from time import strftime
import os
import json
import tablib
import queue

from self_service_terminal.constants import *

# TEMP: Define the settings as the first entry of all Terminal_Settings
# settings = list(Terminal_Settings.objects.all())[0]


def get_settings():
    return Terminal_Settings.objects.get(title='settings')


def index(request):
    """Render and return the homepage.

    If more then BUTTONS_PER_PAGE submenus and subforms are present, render
    additional pages with the remaining buttons, which can be accessed by
    pressing navigation buttons on the left and right side of the screen.
    """
    settings = get_settings()

    homepage_id = settings.homepage.pk
    homepage = settings.homepage

    submenus = list(Menu.objects.filter(parent_menu=homepage_id))
    subforms = list(Form.objects.filter(parent_menu=homepage_id))

    paginator = Paginator(submenus + subforms, BUTTONS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    for i in range(len(page_obj.object_list)):
        page_obj.object_list[i] = {
            'object': page_obj.object_list[i],
            'is_menu': isinstance(page_obj.object_list[i], Menu),
            'is_form': isinstance(page_obj.object_list[i], Form)
        }

    context = {
        'settings': settings,
        'menu': homepage,
        'page_obj': page_obj
    }
    return render(request, 'self_service_terminal/menu.html', context)


def menu(request, menu_id=None, menu_title=None):
    """Render and return the menu site with the primary key <menu_id>.

    If more then BUTTONS_PER_PAGE submenus and subforms are present, render
    additional pages with the remaining buttons, which can be accessed by
    pressing navigation buttons on the left and right side of the screen.
    """
    settings = get_settings()

    menu = Menu.objects.get(pk=menu_id)
    submenus = list(Menu.objects.filter(parent_menu=menu_id))
    subforms = list(Form.objects.filter(parent_menu=menu_id))

    # Fill the paginator with all submenus and subforms
    paginator = Paginator(submenus + subforms, BUTTONS_PER_PAGE)

    # Get the current page from the HTTP Request
    page_number = request.GET.get('page')

    # Get all objects that are allowed on the current page
    page_obj = paginator.get_page(page_number)

    # Add option to test for Menu and Form object
    for i in range(len(page_obj.object_list)):
        page_obj.object_list[i] = {
            'object': page_obj.object_list[i],
            'is_menu': isinstance(page_obj.object_list[i], Menu),
            'is_form': isinstance(page_obj.object_list[i], Form)
        }

    context = {
        'settings': settings,
        'menu': menu,
        'page_obj': page_obj
    }
    return render(request, 'self_service_terminal/menu.html', context)


def formular(request, form_id=None, form_title=None):
    """Render and return the form site with the primary key <form_id>.

    Create a preview image for the PDF to be printed. Then render and return
    the form page.
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
        img_url = settings.insurance_logo.url

    parent_page_number = request.GET.get('page')

    context = {
        'settings': settings,
        'form': form,
        'img_path': img_url,
        'parent_page_number': parent_page_number
    }
    return render(request, 'self_service_terminal/formular.html', context)


def print_formular(request, form_id=None):
    """Run the print method of the given form object and return a HTTP 204
    No Content response.
    """
    form = Form.objects.get(pk=form_id)
    if form.pdffile.name != 'forms/default.pdf':
        form.print_form()
        return HttpResponse(status=204)
    else:
        return HttpResponse('No PDF file deposited.', status=404)

def export_view(request=HttpRequest(), return_string=False, path=EXPORT_PATH):
    # Get menu that has no parent
    root = Menu.objects.filter(parent_menu=None)[0]
    
    # Breadth-first search (BFS) on the menus
    # This is necessary to retain the order of the menus when importing then
    q = queue.Queue()
    discovered = [root]
    export_list = list()
    q.put(root)
    while not q.qsize() == 0:
        menu = q.get()
        export_list.append(menu)
        for submenu in Menu.objects.filter(parent_menu=menu.pk):
            if submenu not in discovered:
                discovered.append(submenu)
                q.put(submenu)

    # Get the settings and forms
    settings = Terminal_Settings.objects.get(title='settings')
    forms = list(Form.objects.all())

    # Create output dictionary
    output_dictionary = {
        "menus" : list(),
        "settings" : list(),
        "forms" : list()
    }

    # Add all menus to the output_dictionary
    for menu in export_list:
        menu = vars(menu)
        menu.pop('_state')
        output_dictionary['menus'].append(menu)

    # Add the settings to the output_dictionary
    settings = vars(settings)
    settings.pop('_state')
    output_dictionary['settings'].append(settings)

    # Add all forms to the output_dictionary
    for form in Form.objects.all():
        form = vars(form)
        form.pop('_state')
        form.pop('upload_date')
        form.pop('last_changed')
        output_dictionary['forms'].append(form)
    
    # Create output json string
    output_json = json.dumps(output_dictionary, indent=4)

    date = strftime('%Y-%m-%d')

    if return_string:
        return output_json
    else:
        if not path.exists():
            path.mkdir()
        with open(path.joinpath(date + '_export.json'), mode='w') as fp:
            fp.write(output_json)


# def export_view(request=HttpRequest(), return_string=False, path=EXPORT_PATH):
#     """Export settings, menus and forms.

#     Export the files YYYY-MM-DD_settings-export.json,
#     YYYY-MM-DD_menu-export.json and YYYY-MM-DD_form-export.json to the
#     directory "path".
#     If return_json is set True return the tuple
#     (settings-export-json, menu-export-json, form-export-json) as strings
#     instead.
#     """
#     settings_dataset = Terminal_SettingsResource().export()

#     # Remove the homepage key from the settings that are going to be exported
#     settings_dataset_dict = json.loads(settings_dataset.json)
#     settings_dataset_dict[0].pop('homepage')

#     # Prepare the settings json file
#     settings_dataset_json = json.dumps(settings_dataset_dict)


#     settings = Terminal_Settings.objects.get(title='settings')
#     homepage = settings.homepage
#     menu_queryset = Menu.objects.exclude(pk=settings.homepage.pk)
#     menu_dataset = MenuResource().export(queryset=menu_queryset)
#     form_dataset = FormResource().export()
    
#     date = strftime('%Y-%m-%d')
    
#     # Format the json strings to make them human readable
#     settings_dataset_json = json.dumps(json.loads(settings_dataset_json), indent=4)
#     menu_dataset_json = json.dumps(json.loads(menu_dataset.json), indent=4)
#     form_dataset_json = json.dumps(json.loads(form_dataset.json), indent=4)

#     # Either return the exported strings directly or write them to the path
#     if return_string:
#         return (settings_dataset_json, menu_dataset_json, form_dataset_json)
#     else:
#         if not path.exists():
#             path.mkdir()
#         with open(path.joinpath(date + '_settings_export.json'), mode='w') as fp:
#             fp.write(settings_dataset_json)
#         with open(path.joinpath(date + '_menu-export.json'), mode='w') as fp:
#             fp.write(menu_dataset_json)
#         with open(path.joinpath(date + '_form-export.json'), mode='w') as fp:
#             fp.write(form_dataset_json)

# def import_view(request=HttpRequest(), import_string=False, settings_file=None,
#                 menu_file=None, form_file=None):
#     """Import settings, menus and forms.
#     """
#     if not import_string:
#         with open(menu_file, mode='r') as fp:
#             menu_json = json.load(fp)
#         with open(form_file, mode='r') as fp:
#             form_json = json.load(fp)
#     else:
#         menu_json = menu_file
#         form_json = form_file

#     menu_dataset = tablib.Dataset()
#     form_dataset = tablib.Dataset()
#     menu_dataset.load(str(menu_json))
#     form_dataset.load(str(form_json))

#     MenuResource().import_data(menu_dataset)
#     FormResource().import_data(form_dataset)


# Testview für die Django Templatesprache
def menu_template_test(request, menu_id=None, menu_title=None):
    """Only for testing purposes."""
    settings = get_settings()
    if menu_id:
        menu = Menu.objects.get(pk=menu_id)
        submenus = list(Menu.objects.filter(parent_menu=menu_id))
        subforms = list(Form.objects.filter(parent_menu=menu_id))

        # Fill the paginator with all submenus and subforms
        paginator = Paginator(submenus + subforms, BUTTONS_PER_PAGE)

        # Get the current page from the HTTP Request
        page_number = request.GET.get('page')
        # Get all objects that are allowed on the current page
        page_obj = paginator.get_page(page_number)

        # Add option to test for Menu and Form object
        for i in range(len(page_obj.object_list)):
            page_obj.object_list[i] = {
                'object': page_obj.object_list[i],
                'is_menu': isinstance(page_obj.object_list[i], Menu),
                'is_form': isinstance(page_obj.object_list[i], Form)
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

        paginator = Paginator(submenus + subforms, BUTTONS_PER_PAGE)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        for i in range(len(page_obj.object_list)):
            page_obj.object_list[i] = {
                'object': page_obj.object_list[i],
                'is_menu': isinstance(page_obj.object_list[i], Menu),
                'is_form': isinstance(page_obj.object_list[i], Form)
            }

        context = {
            'settings': settings,
            'menu': homepage,
            'page_obj': page_obj
        }
        return render(request, 'self_service_terminal/dtl_test.html', context)
