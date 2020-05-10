from django.contrib import admin

from .models import Form, Menu

class FormAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Übergeordnetes Menü', {'fields': ['parent_menu']}),
        ('Anzeigen',            {'fields': ['show_on_frontend']}),
        ('Details',             {'fields': ['form_title', 'description']})
        ]
    list_display = ['form_title', 'time_since_last_updated', 'upload_date', 'last_changed']
    list_filter = ['upload_date','last_changed']
        
class MenuAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Oberkategorie',    {'fields': ['parent_menu']}),
        ('Beschreibung',     {'fields': ['menu_title', 'menu_text']})
    ]

admin.site.register(Form, FormAdmin)
admin.site.register(Menu, MenuAdmin)