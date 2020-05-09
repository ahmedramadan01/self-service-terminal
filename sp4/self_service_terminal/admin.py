from django.contrib import admin

from .models import Form, Menu

class FormAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Übergeordnetes Menü', {'fields': ['parent_menu']}),
        ('Anzeigen',            {'fields': ['show_on_frontend']}),
        ('Details',             {'fields': ['form_title', 'description']})
        ]
        
admin.site.register(Form, FormAdmin)

admin.site.register(Menu)