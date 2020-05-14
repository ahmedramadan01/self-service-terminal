from django.test import TestCase
from .models import Menu, Form
import datetime

retstr = "Zuletzt geändert vor {days} Tagen, {hours} Stunden, {minutes} Minuten."

class FormTestCase(TestCase):
    def setUp(self):
        Menu.objects.create(menu_title='Root', menu_text='Wurzelmenü')
        root = Menu.objects.get(menu_title='Root')
        Form.objects.create(form_title='1', parent_menu=root)
        Form.objects.create(form_title='2', parent_menu=root, upload_date=datetime.datetime(2000, 1, 1), last_changed=datetime.datetime(1999, 1, 1))
    
    def test_menu_form_interaction(self):
        root = Menu.objects.get(menu_title='Root')
        form = Form.objects.get(form_title='1')
        self.assertEqual(root.menu_text, 'Wurzelmenü')
        self.assertEqual(form.parent_menu, root)

    def test_time_since_last_updated(self):
        all_forms = Form.objects.all()
        for form in all_forms:
            (days, hours, minutes) = form.time_since_last_updated()
            self.assertGreaterEqual(days, 0)
            self.assertLess(hours, 24)
            self.assertGreaterEqual(hours, 0)
            self.assertLess(minutes, 60)
            self.assertGreaterEqual(minutes, 0)