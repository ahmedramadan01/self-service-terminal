"""
Automated Tests.

Test database structure:
    - Settings >-|
    - Menu <-----| Homepage
        |
        -<- Submenu
        |
        -<- Form

Configurations for Settings:
    1. Homepage set/not set
    2. colorval_* set/not set (default?)
    3. *_logo set/not set

Configurations for Menu:
    1. parent_menu set/not set

Configurations for Submenu:
    1. parent_menu set to Menu

Configurations for Form:
    1. pdffile set/not set
    2. show-on-frontend True/False

General tests for every different configuration:
    1. Return of Status Code 200 for
        - /
        - /menu/<pk-of-Menu>
        - /menu/<pk-of-Submenu>
        - /form/<pk-of-Form>
    2. Return of Status Code 204 for
        - /form/<pk-of-Form>/print
    3. Check for return code of lpr-command == 0
    4. (T0010) Test the user navigation:
        Depth-first-search via menu and form URLs starting from the
        homepage.
    5. (T0010) Check tree structure via Primary Keys against proposed structure
        in setUp method.
    6. (T0030) If no PDF is set in the admin panel, no PDF should be printed out
        and an error message should be displayed.
    7. (T0040) Test Upload of a PDF in the admin panel:
        - check if files/forms/<pdf_name> exists
        - check files/forms/<pdf_name> is in database form entry 
        (form.url, form.path?)
    8. (T0050) Add Form object with attributes and
        - Check if values of attributes are saved in database.
        - Change these values via the admin panel and check if the new values 
        are present in the database.
    9. (T0060) Delete Form object via admin panel and
        - check if database entries have been deleted.
        - check if foreign key entries have been deleted.
    10. (T0070) Change color values via admin panel
        - check if color values have been changed in database.
        - check if colors have changed in frontend.
        Upload logos via admin panel and
        - check if files/images/<logo_name> exists in file system.
        - check if database entries have been added for the logos.
        - check if logos are present in the frontend.
    11. (T0080) Export and Import
        Run the export function and
        - check if exported json file exists in file system at
        EXPORT_PATH/export/<YYYY-MM-DD_menu-export.json> and
        EXPORT_PATH/export/<YYYY-MM-DD_form-export.json>.
        - assert that the exported json files are equal to the expected ones.
        Run the import function on a database with only the settings and
        homepage object and
        - check the database if the new objects exists.
        - check the values of all objects against how they should be set.
    12. (T0090) Pagination test
        Create a menu with more then 5 submenus and forms.
        - Check via regex if the links for pagination appear.
        - Check via URL parameters if pagination works.

TODO document:
- input = used attributes
- expected_output
- output = actual_output
"""
from subprocess import run
from pathlib import Path
import os
import re
import json

from django.test import TestCase, Client
from self_service_terminal.models import Terminal_Settings, Menu, Form
from self_service_terminal.views import get_settings, export_view, import_view
from self_service_terminal.constants import *


class DefaultTestCase(TestCase):
    """Default test case.

    This class describes the default test case. It can be subclassed to
    overwrite the values in the setUp method. At least all values from this
    setUp method must be present in the subclass's setUp method, otherwise
    tests from DefaultTestCase will fail.
    If new values are added to the subclass in the setUp method, they can only
    be used in the test methods of the subclass.
    """

    def setUp(self):
        self.terminal_settings = Terminal_Settings.objects.create(
            title='settings')
        self.terminal_settings.save()
        self.menu = Menu.objects.create(menu_title='default_menu')
        self.menu.save()
        self.submenu = Menu.objects.create(
            parent_menu=self.menu,
            menu_title='default_submenu'
        )
        self.submenu.save()
        # T0040
        self.form = Form.objects.create(
            parent_menu=self.menu,
            pdffile='forms/form.pdf',
            show_on_frontend=True,
            form_title='default_form'
        )
        self.form.save()
        self.form2 = Form.objects.create(
            parent_menu=self.submenu,
            show_on_frontend=True,
            form_title='second_form'
        )
        self.form2.save()
        self.terminal_settings.homepage = self.menu
        self.terminal_settings.save()
        self.c = Client()

    def test_homepage_availability(self):
        homepage_response = self.c.get('/')
        self.assertEqual(homepage_response.status_code, 200)

        menu_response = self.c.get('/menu/' + str(self.menu.pk) + '/')
        self.assertEqual(menu_response.status_code, 200)

        homepage_menu_response = self.c.get(
            '/menu/' + str(self.terminal_settings.homepage.pk) + '/')
        self.assertEqual(homepage_menu_response.status_code, 200)

        self.assertHTMLEqual(
            homepage_menu_response.content.decode(), menu_response.content.decode())

    def test_menu_availability(self):
        for m in Menu.objects.all():
            response = self.c.get('/menu/' + str(m.pk) + '/')
            self.assertEqual(response.status_code, 200)

    def test_form_availability(self):
        for f in Form.objects.all():
            response = self.c.get('/form/' + str(f.pk) + '/')
            self.assertEqual(response.status_code, 200)

    def test_print_return_code(self):
        """ (T0020)
        """
        for f in Form.objects.all():
            response = self.c.get('/form/' + str(f.pk) + '/print')
            if f.pdffile.name == 'forms/default.pdf':
                self.assertEqual(response.status_code, 404)
            else:
                self.assertEqual(response.status_code, 200)
        run(['lprm', '-'])

    def test_cups_availability(self):
        """Test the availability of the CUPS Server

        Run the tests in an environment with the locale set to 'en_US.utf8'
        equal results on all machines.
        """
        locale = 'en_US.UTF-8'
        env = ['env', 'LANG=' + locale]
        command_is_running = ['lpstat', '-r']
        command_default = ['lpstat', '-d']

        response = run(env + command_is_running, capture_output=True)
        self.assertEqual(response.stdout, b'scheduler is running\n')

        response = run(env + command_default, capture_output=True)
        self.assertNotEqual(
            response.stdout,
            b'no system default destination\n')

    def test_get_settings(self):
        self.assertEqual(
            type(get_settings()), 
            Terminal_Settings
        )
        self.assertEqual(get_settings(), 
        Terminal_Settings.objects.get(title='settings'))

    def test_user_navigation(self):
        """ (T0010) Simulate a user navigating through the pages.
        """
        # get homepage primary key
        homepage = Menu.objects.get(pk=self.terminal_settings.homepage.pk)
        homepage_response = self.c.get('/menu/' + str(homepage.pk) + '/')
        self.assertEqual(homepage_response.status_code, 200)
        
        # Depth-First-Search
        submenu_stack = [homepage]
        discovered = list()
        while len(submenu_stack) > 0:
            menu = submenu_stack.pop()
            if not menu in discovered:
                discovered.append(menu)
                menu_response = self.c.get('/menu/' + str(menu.pk) + '/')
                self.assertEqual(menu_response.status_code, 200)
                submenus = list(Menu.objects.filter(parent_menu=menu.pk))
                subforms = list(Form.objects.filter(parent_menu=menu.pk))
                for entry in submenus:
                    submenu_stack.append(entry)
                for entry in subforms:
                    form_response = self.c.get('/form/' + str(entry.pk) + '/')
                    self.assertEqual(form_response.status_code, 200)
                    
    def test_menu_1(self):
        r = self.c.get('/menu/1/')
        self.assertEqual(r.status_code, 200)

    def test_pdf_file_exists(self):
        """ (T0040)
        """
        for form_entry in Form.objects.all():
            path = Path(form_entry.pdffile.path)
            self.assertTrue(path.exists())

    def test_pdf_database_relation(self):
        """ (T0050)
        """
        self.custom_form = Form.objects.create(
            parent_menu=self.submenu,
            pdffile="forms/form.pdf",
            form_title='custom_form',
            description='nothing to see here'
        )
        self.custom_form.save()
        try:
            # Test if the objects has been initialized correctly
            self.assertEqual(self.custom_form.parent_menu, self.submenu)
            self.assertEqual(self.custom_form.name, 'forms/form.pdf')
            self.assertEqual(self.custom_form.url, '/files/forms/form.pdf')
            self.assertEqual(self.custom_form.pdffile.name, 'forms/form.pdf')
            self.assertEqual(self.custom_form.pdffile.url, '/files/forms/form.pdf')
            self.assertEqual(self.custom_form.form_title, 'custom_form')
            self.assertEqual(self.custom_form.description, 'nothing to see here')

            # Change parameters of pdf file and test if they have changed
            form = Form.objects.get(form_title='custom_form')
            form.form_title = 'different title'
            form.description = 'a lot ot see here'
            form.save()
            self.assertEqual(self.custom_form.form_title, 'different title')
            self.assertEqual(self.custom_form.description, 'a lot to see here')
        except:
            pass
        finally:
            self.custom_form.delete()
        
    def test_change_color_values(self):
        """ (T0070) Change the color values.
        """
        color = 'red'
        t = self.terminal_settings
        t.colorval_nav_bar = color
        t.colorval_heading = color
        t.colorval_button = color
        t.colorval_return_button = color
        t.save()

        settings = Terminal_Settings.objects.get(title='settings')
        self.assertEqual(settings.colorval_nav_bar, 'red')
        self.assertEqual(settings.colorval_heading, 'red')
        self.assertEqual(settings.colorval_button, 'red')
        self.assertEqual(settings.colorval_return_button, 'red')
        
    def test_pagination(self):
        """ (T0090)
        """
        number_menus = 10
        for i in range(number_menus):
            Menu.objects.create(
                menu_title='pagination_menu_' + str(i),
                parent_menu=self.submenu
            )
            
        response = self.c.get('/menu/' + str(self.submenu.pk) + '/?page=1')
        self.assertEqual(response.status_code, 200)
        response = response.content.decode()
        for i in range(5):
            self.assertIn('pagination_menu_' + str(i), response)

        response = self.c.get('/menu/' + str(self.submenu.pk) + '/?page=2')
        self.assertEqual(response.status_code, 200)
        response = response.content.decode()
        for i in range(5, 10):
            self.assertIn('pagination_menu_' + str(i), response)
        


class UnconnectedConfiguration(DefaultTestCase):
    def setUp(self):
        self.terminal_settings = Terminal_Settings.objects.create(
            title='settings')
        self.terminal_settings.save()
        self.menu = Menu.objects.create(menu_title='default_menu')
        self.menu.save()
        self.submenu = Menu.objects.create(
            parent_menu=self.menu,
            menu_title='default_submenu'
        )
        self.submenu.save()
        self.form = Form.objects.create(
            parent_menu=self.menu,
            pdffile='forms/form.pdf',
            show_on_frontend=True,
            form_title='default_form'
        )
        self.form.save()

        # Here's the difference:
        self.terminal_settings.homepage = self.submenu

        self.terminal_settings.save()
        self.c = Client()
    
    def test_homepage_availability(self):
        homepage_response = self.c.get('/')
        self.assertEqual(homepage_response.status_code, 200)

        submenu_response = self.c.get('/menu/' + str(self.submenu.pk) + '/')
        self.assertEqual(submenu_response.status_code, 200)

        homepage_menu_response = self.c.get(
            '/menu/' + str(self.terminal_settings.homepage.pk) + '/')
        self.assertEqual(homepage_menu_response.status_code, 200)

        self.assertHTMLEqual(
            homepage_menu_response.content.decode(), submenu_response.content.decode())


class ProductionCase(DefaultTestCase):
    def setUp(self):
        self.terminal_settings = Terminal_Settings.objects.create(
            title='settings')
        self.terminal_settings.save()
        self.menu = Menu.objects.create(menu_title='default_menu')
        self.menu.save()
        self.submenu = Menu.objects.create(
            parent_menu=self.menu,
            menu_title='default_submenu'
        )
        self.submenu.save()
        self.form = Form.objects.create(
            parent_menu=self.menu,
            pdffile='forms/form.pdf',
            show_on_frontend=True,
            form_title='default_form'
        )
        self.form.save()
        self.terminal_settings.homepage = self.menu
        self.terminal_settings.save()
        self.c = Client()

    def test_debug_false(self):
        with self.settings(Debug=False):
            response = self.c.get('/')
            self.assertEqual(response.status_code, 200)

class PaginationTestCase(TestCase):
    """ (T0090)
    """
    def setUp(self):
        self.terminal_settings = Terminal_Settings.objects.create(
            title='settings')
        self.terminal_settings.save()

        self.menu = Menu.objects.create(menu_title='homepage')
        self.menu.save()

        self.submenus = list()
        for i in range(6):
            submenu = Menu.objects.create(
                menu_title='sub' + str(i+1),
                parent_menu=self.menu
            )
            submenu.save()
            self.submenus.append(submenu)

        self.c = Client()
    
    def test_pagination_existence(self):
        pagination_link_re = re.compile(r'(?s)<a .* href="\?page=2".*>')
        menu_response = self.c.get('/menu/' + str(self.menu.pk) + '/')
        html_site = menu_response.content.decode()
        self.assertTrue(pagination_link_re.search(html_site))
        
        pagination_link_re = re.compile(r'(?s)<a .* href="\?page=1".*>')
        menu_response = self.c.get('/menu/' + str(self.menu.pk) + '/?page=2')
        html_site = menu_response.content.decode()
        self.assertTrue(pagination_link_re.search(html_site))
    
    def test_different_pagination_sites(self):
        page_one = self.c.get('/menu/' + str(self.menu.pk) + '/?page=1')
        page_two = self.c.get('/menu/' + str(self.menu.pk) + '/?page=2')
        page_one = page_one.content.decode()
        page_two = page_two.content.decode()
        self.assertHTMLNotEqual(page_one, page_two)


class ExportImportTestCase(TestCase):
    def setUp(self):
        self.terminal_settings = Terminal_Settings.objects.create(
            title='settings')
        self.terminal_settings.save()
        self.menu = Menu.objects.create(menu_title='default_menu')
        self.menu.save()
        self.submenu = Menu.objects.create(
            parent_menu=self.menu,
            menu_title='default_submenu'
        )
        self.submenu.save()
        # T0040
        self.form = Form.objects.create(
            parent_menu=self.menu,
            pdffile='forms/form.pdf',
            show_on_frontend=True,
            form_title='default_form'
        )
        self.form.save()
        self.form2 = Form.objects.create(
            parent_menu=self.submenu,
            show_on_frontend=True,
            form_title='second_form'
        )
        self.form2.save()
        self.terminal_settings.homepage = self.menu
        self.terminal_settings.save()
        self.c = Client()
        self.expected_object = {
            'menus': [
                {
                    "id": 1,
                    "parent_menu_id": None,
                    "menu_title": "default_menu",
                    "menu_text": ""
                },
                {
                    "id": 2,
                    "parent_menu_id": 1,
                    "menu_title": "default_submenu",
                    "menu_text": ""
                }
            ],
            'settings': [
                {
                    "id": 1,
                    "title": "settings",
                    "description": None,
                    "colorval_nav_bar": "",
                    "colorval_heading": "",
                    "colorval_text": "",
                    "colorval_button": "",
                    "colorval_return_button": "",
                    "institute_logo": "images/institute_logo.png",
                    "insurance_logo": "images/insurance_logo.png"
                }
            ],
            'forms': [
                {
                    "id": 1,
                    "parent_menu_id": 1,
                    "pdffile": "forms/form.pdf",
                    "show_on_frontend": True,
                    "form_title": "default_form",
                    "description": ""
                },
                {
                    "id": 2,
                    "parent_menu_id": 2,
                    "pdffile": "forms/default.pdf",
                    "show_on_frontend": True,
                    "form_title": "second_form",
                    "description": ""
                }
            ]
        }


    def test_export_as_string(self):
        """ (T0080)
        """
        exported_string = export_view(return_string=True)
        exported_object = json.loads(exported_string)
        self.assertEqual(self.expected_object, exported_object)

    def test_export_import_in_file(self):
        """ (T0080)
        """
        export_view()

        # Delelte all entries in database
        for entry in Menu.objects.all():
            entry.delete()
        for entry in Terminal_Settings.objects.all():
            entry.delete()
        for entry in Form.objects.all():
            entry.delete()
        
        # import the newest data in the export directory
        path = EXPORT_PATH
        exported_files = list(path.glob('**/*.zip'))
        file_last_changed = dict()
        for entry in exported_files:
            file_last_changed[entry] = os.path.getctime(entry)
        import_view(imported_data=max(file_last_changed))

        # Check if the database is filled and reachable
        db_structure = export_view(return_string=True)
        db_structure = json.loads(db_structure)
        self.assertEqual(db_structure, self.expected_object)

        for menu in Menu.objects.all():
            response = self.c.get('/menu/' + str(menu.pk) + '/')
            self.assertEqual(response.status_code, 200)
        for form in Form.objects.all():
            response = self.c.get('/form/' + str(form.pk) + '/')
            self.assertEqual(response.status_code, 200)
            response = self.c.get('/form/' + str(form.pk) + '/view')
            self.assertEqual(response.status_code, 200)

    def test_number_of_db_entries_when_import_as_string(self):
        number_menus_old = len(Menu.objects.all())
        number_forms_old = len(Form.objects.all())

        exported_data = export_view(return_string=True)
        for entry in Menu.objects.all():
            entry.delete()
        for entry in Terminal_Settings.objects.all():
            entry.delete()
        for entry in Form.objects.all():
            entry.delete()
        import_view(import_string=True, imported_data=exported_data)
        
        number_menus_new = len(Menu.objects.all())
        number_forms_new = len(Form.objects.all())

        self.assertEqual(number_menus_old, number_forms_new)
        self.assertEqual(number_forms_old, number_forms_new)

class NoPdfSetTestCase(TestCase):
    """ (T0030)
    """
    def setUp(self):
        self.terminal_settings = Terminal_Settings.objects.create(
            title='settings')
        self.terminal_settings.save()
        self.menu = Menu.objects.create(menu_title='default_menu')
        self.menu.save()
        self.submenu = Menu.objects.create(
            parent_menu=self.menu,
            menu_title='default_submenu'
        )
        self.submenu.save()
        # no PDF set
        self.form = Form.objects.create(
            parent_menu=self.menu,
            show_on_frontend=True,
            form_title='default_form'
        )
        self.form.save()
        self.form2 = Form.objects.create(
            parent_menu=self.submenu,
            show_on_frontend=True,
            form_title='second_form'
        )
        self.form2.save()
        self.terminal_settings.homepage = self.menu
        self.terminal_settings.save()
        self.c = Client()        

    def test_no_pdf_error(self):
        for form_object in Form.objects.all():
            response = self.c.get('/form/' + str(form_object.pk) + '/print')
            self.assertEqual(response.status_code, 404)
            response_html = response.content.decode()
            self.assertHTMLEqual(response_html, 'No PDF file deposited.')
        response = self.c.get('/form/' + str(self.form.pk) + '/print')
        self.assertEqual(response.status_code, 404)
        response_html = response.content.decode()
        self.assertHTMLEqual(response_html, 'No PDF file deposited.')

