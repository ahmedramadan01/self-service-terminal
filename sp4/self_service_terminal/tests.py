"""
Automated Tests.

Test database structure:
    - Settings >-|
    - Menu <-----| Homepage
        |
        -<- Submenu
        |
        -<- Form

General tests for every different configuration:
    1. Return of Status Code 200 for
        - /
        - /menu/<pk-of-Menu>
        - /menu/<pk-of-Submenu>
        - /form/<pk-of-Form>
    2. Return of Status Code 204 for
        - /form/<pk-of-Form>/print
    and check for return code of lpr-command == 0

Configurations for Settings:
    1. Homepage set/not set
    2. colorval_* set/not set (default?)
    3. *_logo set/not set

Configurations for Menu:
    1. parent_menu set/not set

Configurations for Submenu:
    1. parent_menu set to Menu

Configuration for Form:
    1. pdffile set/not set
    2. show-on-frontend True/False
"""

from django.test import TestCase, Client
from self_service_terminal.models import Terminal_Settings, Menu, Form


class DefaultTestCase(TestCase):
    def setUp(self):
        self.settings = Terminal_Settings.objects.create(
            title='default_settings')
        self.settings.save()
        self.menu = Menu.objects.create(
            settings=self.settings, menu_title='default_menu')
        self.menu.save()
        self.submenu = Menu.objects.create(
            settings=self.settings,
            parent_menu=self.menu,
            menu_title='default_submenau'
        )
        self.submenu.save()
        self.form = Form.objects.create(
            parent_menu=self.menu,
            pdffile='forms/form.pdf',
            show_on_frontend=True,
            form_title='default_form'
        )
        self.form.save()
        self.settings.homepage = self.menu
        self.settings.save()
        self.c = Client()

    def test_homepage_availability(self):
        homepage_response = self.c.get('/')
        self.assertEqual(homepage_response.status_code, 200)
        self.assertEqual(self.settings.homepage.pk, 1)

        self.assertEqual(self.menu.pk, 1)
        menu_response = self.c.get('/menu/' + str(self.menu.pk))
        self.assertEqual(menu_response.status_code, 200)

        self.assertHTMLEqual(
            str(homepage_response.content), str(menu_response.content))
