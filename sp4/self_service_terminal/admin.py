from django.contrib import admin

from .models import Form, Menu, Startpage, Design

class DesignAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Farbe',           {'fields': ['colorval']}),
        ('Logo',            {'fields': ['institute_logo']})
    ]

class StartpageAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Titel',           {'fields': ['start_title']}),
        ('Text',            {'fields': ['start_text']})
    ]

class FormInline(admin.StackedInline):
    model = Form
    extra = 0

class MenuAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Startseite',       {'fields': ['startpage']}),
        ('Oberkategorie',    {'fields': ['parent_menu']}),
        ('Beschreibung',     {'fields': ['menu_title', 'menu_text']})
    ]
    inlines = [FormInline]

class FormAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Übergeordnetes Menü', {'fields': ['parent_menu']}),
        ('Anzeigen',            {'fields': ['show_on_frontend']}),
        ('Details',             {'fields': ['form_title', 'description']}),
        ('Dateipfad',           {'fields': ['pdffile']})
        ]
    list_display = ['form_title', 'time_since_last_updated_str', 'upload_date', 'last_changed']
    list_filter = ['upload_date','last_changed']

admin.site.register(Design, DesignAdmin)
admin.site.register(Startpage, StartpageAdmin)
admin.site.register(Menu, MenuAdmin)
# admin.site.register(Form, FormAdmin)