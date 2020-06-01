from django.contrib import admin

from .models import Form, Menu, Homepage

from import_export.admin import ImportExportModelAdmin

class MenuInline(admin.TabularInline):
    model = Menu
    extra = 0

class FormInline(admin.TabularInline):
    model = Form
    extra = 0



@admin.register(Homepage)
class HomepageAdmin(ImportExportModelAdmin):
    fieldsets = [
        ('Farbe',           {'fields': ['colorval']}),
        ('Logo',            {'fields': ['institute_logo']})
    ]



@admin.register(Menu)
class MenuAdmin(ImportExportModelAdmin):
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


# admin.site.register(Homepage, HomepageAdmin)
# admin.site.register(Menu, MenuAdmin)