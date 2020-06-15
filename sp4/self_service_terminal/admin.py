"""Customizations for the admin site.

This document defines among other things which fields appear on the admin page
and can be edited.
"""

from django.contrib import admin
from .models import Form, Menu, Terminal_Settings
from import_export.admin import ImportExportModelAdmin
from django.contrib.admin import AdminSite

class MyAdminSite(AdminSite):
    site_header = 'Monty python adminstration'
admin_site = MyAdminSite(name='myadmin')
admin_site.register(Terminal_Settings)
admin_site.register(Form)
admin_site.register(Menu)

admin.site.site_header = 'Admin Tutorial Dashboard'
class MenuInline(admin.TabularInline):
    model = Menu
    extra = 0


class FormInline(admin.TabularInline):
    model = Form
    extra = 0


@admin.register(Terminal_Settings)
class Terminal_SettingsAdmin(ImportExportModelAdmin):
    fieldsets = [
        ('Startseite', {'fields': ['homepage']}),
        ('Beschreibung', {'fields': ['title', 'description']}),
        ('Farbe',
            {'fields': [
                'colorval_nav_bar',
                'colorval_heading',
                'colorval_text',
                'colorval_button',
                'colorval_zurueck_button']
             }),
        ('Logos', {'fields': ['institute_logo', 'insurance_logo']})
    ]


@admin.register(Menu)
class MenuAdmin(ImportExportModelAdmin):
    fieldsets = [
        ('Startseite', {'fields': ['settings']}),
        ('Oberkategorie', {'fields': ['parent_menu']}),
        ('Beschreibung', {'fields': ['menu_title', 'menu_text']})
    ]
    inlines = [MenuInline, FormInline]


@admin.register(Form)
class FormAdmin(ImportExportModelAdmin):
    fieldsets = [
        ('Übergeordnetes Menü', {'fields': ['parent_menu']}),
        ('Anzeigen', {'fields': ['show_on_frontend']}),
        ('Details', {'fields': ['form_title', 'description']}),
        ('Dateipfad', {'fields': ['pdffile']})
    ]
    list_display = ['form_title', 'time_since_last_updated_str',
                    'upload_date', 'last_changed']
    list_filter = ['upload_date', 'last_changed']
