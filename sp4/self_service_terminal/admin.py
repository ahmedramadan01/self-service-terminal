from django.contrib import admin

from .models import Form, Menu, Terminal_Settings

class MenuInline(admin.TabularInline):
    model = Menu
    extra = 0

class FormInline(admin.TabularInline):
    model = Form
    extra = 0

@admin.register(Terminal_Settings)
class Terminal_SettingsAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Farbe',           {'fields': ['colorval_nav_bar', 'colorval_heading', 'colorval_text', 'colorval_button', 'colorval_zueruck_button']}),
        ('Logos',            {'fields': ['institute_logo', 'krankenkasse_logo']})

    ]

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Startseite',       {'fields': ['homepage']}),
        ('Oberkategorie',    {'fields': ['parent_menu']}),
        ('Beschreibung',     {'fields': ['menu_title', 'menu_text']})
    ]
    inlines = [MenuInline, FormInline]

class FormAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Übergeordnetes Menü', {'fields': ['parent_menu']}),
        ('Anzeigen',            {'fields': ['show_on_frontend']}),
        ('Details',             {'fields': ['form_title', 'description']}),
        ('Dateipfad',           {'fields': ['pdffile']})
        ]
    list_display = ['form_title', 'time_since_last_updated_str', 'upload_date', 'last_changed']
    list_filter = ['upload_date','last_changed']

# admin.site.register(Terminal_Settings, Terminal_SettingsAdmin)
# admin.site.register(Menu, MenuAdmin)