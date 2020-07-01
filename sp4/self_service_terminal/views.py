from django.core.paginator import Paginator
from django.shortcuts import render, HttpResponse
from django.http import HttpRequest
from self_service_terminal.models import Menu, Form, Terminal_Settings

from pdf2image import convert_from_path
from datetime import datetime
from time import strftime
from shutil import copytree, copy2, rmtree
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED, is_zipfile
import os
import json
import tablib
import queue

from self_service_terminal.constants import *

def get_settings():
    return Terminal_Settings.objects.get(title='settings')

def get_homepage():
    return Menu.objects.filter(parent_menu=None)[0]


def index(request):
    """Render and return the homepage.

    If more then BUTTONS_PER_PAGE submenus and subforms are present, render
    additional pages with the remaining buttons, which can be accessed by
    pressing navigation buttons on the left and right side of the screen.
    """
    settings = get_settings()

    homepage = get_homepage()
    homepage_id = homepage.pk

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
        'is_homepage': True,
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
    homepage = get_homepage()

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
        'is_homepage': menu.pk == homepage.pk,
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

def export_view(request=HttpRequest(), return_string=False, path=EXPORT_PATH,
                export_as_zip=True):
    """ Export the database entries of settings, menus and forms. Copy all
    files from the director files to the export directory.

    If return_string = True return only the database entries as an
    json-formatted string.
    """
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

    date = strftime('%Y-%m-%d_%H-%M-%S')
    path = path.joinpath(date + '_export')
    json_path = path.joinpath(date + '_export.json')
    file_src = Path(BASE_DIR).joinpath('self_service_terminal').joinpath('files')
    file_dst = path.joinpath(date + '_files')

    if return_string:
        return output_json
    else:
        # Write the output to the file system
        if not path.exists():
            path.mkdir()
        with open(json_path, mode='w') as fp:
            fp.write(output_json)
        copytree(file_src, file_dst, copy_function=copy2)

        if export_as_zip:
            # Compress the directory in a zip file using the DEFLATE method
            with ZipFile(str(path) + '.zip', mode='w', compression=ZIP_DEFLATED) as zipdir:
                zipdir.write(filename=json_path,
                            arcname=date + '_export.json')
                for entry in file_dst.joinpath('forms').iterdir():
                    zipdir.write(filename=entry, arcname='files/forms/' + entry.name)
                for entry in file_dst.joinpath('images').iterdir():
                    zipdir.write(filename=entry, arcname='files/images/' + entry.name)
            rmtree(path)



def import_view(request=HttpRequest(), import_string=False, imported_data=None):
    """ Import the files that have been exported by the export_view.

    This view copies all exported files to the files installation directory,
    deletes all settings, menu and form entries on the database
    and adds the exported settings, menus and forms to the database.
    If import_string = True then imported_data should be a string as returned
    by the export_view if its return_string = True.
    """
    # Set the destination for the files
    file_src = Path(BASE_DIR).joinpath('self_service_terminal').joinpath('files')

    if not import_string:
        # unzip imported_data if it is a zip file
        if is_zipfile(imported_data):
            with ZipFile(imported_data, mode='r', compression=ZIP_DEFLATED) as zipdir:
                imported_data = str(imported_data)
                imported_data = imported_data.strip('.zip')
                imported_data = Path(imported_data)
                zipdir.extractall(Path(BASE_DIR).parent.joinpath('export').joinpath(imported_data.name))

        input_json = ''
        imported_data = Path(imported_data)
        for child in imported_data.iterdir():
            # load the database entries from the export
            if '.json' in str(child):
                with open(child) as fp:
                    input_dict = json.load(fp)
            # copy all of the exported files into the files directory
            # of this installation
            if child.is_dir() and '_files' in str(child):
                for f in child.joinpath('forms').iterdir():
                    copy2(f, file_src.joinpath('forms'))
                for f in child.joinpath('images').iterdir():
                    copy2(f, file_src.joinpath('images'))
    else:
        input_dict = json.loads(imported_data)

    # Delete all entries in the database
    for menu in Menu.objects.all():
        menu.delete()
    for form in Form.objects.all():
        form.delete()
    for settings in Terminal_Settings.objects.all():
        settings.delete()

    # Add the menus of input_dict to the database
    for menu in input_dict['menus']:
        try:
            parent = Menu.objects.get(pk=menu['parent_menu_id'])
            m = Menu.objects.create(
                pk=menu['id'],
                parent_menu=parent,
                menu_title=menu['menu_title'],
                menu_text=menu['menu_text']
            )
        except:
            m = Menu.objects.create(
                pk=menu['id'],
                menu_title=menu['menu_title'],
                menu_text=menu['menu_text']
            )
        finally:
            m.save()
    
    # Add the settings of input_dict to the database
    for settings in input_dict['settings']:
        s = Terminal_Settings.objects.create(
            pk=settings['id'],
            title=settings['title'],
            description=settings['description'],
            colorval_nav_bar=settings['colorval_nav_bar'],
            colorval_heading=settings['colorval_heading'],
            colorval_text=settings['colorval_text'],
            colorval_button=settings['colorval_button'],
            colorval_return_button=settings['colorval_return_button'],
            institute_logo=settings['institute_logo'],
            insurance_logo=settings['insurance_logo']
        )
        s.save()

    # Add the forms of input_dict to the database
    for form in input_dict['forms']:
        try:
            parent = Menu.objects.get(pk=form['parent_menu_id'])
            f = Form.objects.create(
                pk=form['id'],
                parent_menu=parent,
                pdffile=form['pdffile'],
                show_on_frontend=form['show_on_frontend'],
                form_title=form['form_title'],
                description=form['description']
            )
        except:
            f = Form.objects.create(
                pk=form['id'],
                pdffile=form['pdffile'],
                show_on_frontend=form['show_on_frontend'],
                form_title=form['form_title'],
                description=form['description']
            )
        finally:
            f.save()



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

def export_action(modeladmin, request, queryset):
    export_view()
