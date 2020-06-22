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
    and check for return code of lpr-command == 0
"""
from subprocess import run

from django.test import TestCase, Client
from self_service_terminal.models import Terminal_Settings, Menu, Form
from self_service_terminal.views import get_settings, export_view
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
            settings=self.terminal_settings,
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

    def test_homepage_availability(self):
        homepage_response = self.c.get('/')
        self.assertEqual(homepage_response.status_code, 200)

        menu_response = self.c.get('/menu/' + str(self.menu.pk) + '/')
        self.assertEqual(menu_response.status_code, 200)

        homepage_menu_response = self.c.get(
            '/menu/' + str(self.terminal_settings.homepage.pk) + '/')
        self.assertEqual(homepage_menu_response.status_code, 200)

        self.assertHTMLEqual(
            str(homepage_response.content), str(homepage_menu_response.content))

    def test_menu_availability(self):
        for m in Menu.objects.all():
            response = self.c.get('/menu/' + str(m.pk) + '/')
            self.assertEqual(response.status_code, 200)

    def test_form_availability(self):
        for f in Form.objects.all():
            response = self.c.get('/form/' + str(f.pk) + '/')
            self.assertEqual(response.status_code, 200)

    def test_print_return_code(self):
        for f in Form.objects.all():
            response = self.c.get('/form/' + str(f.pk) + '/print')
            self.assertEqual(response.status_code, 204)
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
        self.assertEqual(get_settings(), self.menu.settings)
        self.assertEqual(get_settings(), self.submenu.settings)
        self.assertEqual(get_settings(), 
        Terminal_Settings.objects.get(title='settings'))
    
    def test_default_settings(self):
        self.assertEqual(
            self.terminal_settings.pk,
            self.menu.settings.pk)
        for m in Menu.objects.all():
            self.assertEqual(self.terminal_settings.pk, m.settings.pk)

class UnconnectedConfiguration(DefaultTestCase):
    def setUp(self):
        self.terminal_settings = Terminal_Settings.objects.create(
            title='settings')
        self.terminal_settings.save()
        self.menu = Menu.objects.create(
            settings=self.terminal_settings, menu_title='default_menu')
        self.menu.save()
        self.submenu = Menu.objects.create(
            settings=self.terminal_settings,
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


class ProductionCase(DefaultTestCase):
    def setUp(self):
        self.terminal_settings = Terminal_Settings.objects.create(
            title='settings')
        self.terminal_settings.save()
        self.menu = Menu.objects.create(
            settings=self.terminal_settings, menu_title='default_menu')
        self.menu.save()
        self.submenu = Menu.objects.create(
            settings=self.terminal_settings,
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

"""
class NoSettings(DefaultTestCase):
    def setUp(self):
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
"""
