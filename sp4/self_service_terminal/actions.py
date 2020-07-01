from self_service_terminal.views import export_view, import_view
from self_service_terminal.constants import EXPORT_PATH
import os

def export_action(modeladmin, request, queryset):
    export_view()

def import_action(modeladmin, request, queryset):
    path = EXPORT_PATH
    exported_files = list(path.glob('**/*.zip'))
    file_last_changed = dict()
    for entry in exported_files:
        file_last_changed[entry] = os.path.getctime(entry)
    import_view(imported_data=max(file_last_changed))
