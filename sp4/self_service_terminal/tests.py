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

class AccessTestCase(TestCase):
    def setUp(self):
        self.settings = Terminal_Settings.objects.create(title='Settings1')
        self.menu = Menu.objects.create(settings=self.settings, menu_title='Menu')
        self.submenu = Menu.objects.create(
            settings=self.settings, 
            parent_menu=self.menu,
            menu_title='Submenu'
            )
        self.form = Form.objects.create(
            parent_menu=self.menu,
            pdffile='forms/form.pdf',
            show_on_frontend=True,
            form_title='Form'
        )
        self.settings.homepage = self.menu


    def test_homepage_availability(self):
        c = Client()
        homepage_response = c.get('/menu/1')
        menu_response = c.get('/menu/' + str(self.menu.pk))
        self.assertHTMLEqual(
            str(homepage_response.content), str(menu_response.content))
