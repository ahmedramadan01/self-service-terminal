from self_service_terminal.views import export_view, import_view
from self_service_terminal.constants import EXPORT_PATH

def export_action(modeladmin, request, queryset):
    export_view()

def import_action(modeladmin, request, queryset):
    pass