from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

# TODO Customize error view to automatically return to homepage

urlpatterns = [
    path('', views.index, name='index'),
    path('menu/<int:menu_id>/', views.menu, name="menu_id"),
    path('menu/<str:menu_title>/', views.menu, name="menu_title"),
    path('form/<int:form_id>/', views.formular, name="form_id"),
    path('form/<int:form_id>/print', views.print_formular, name="form_print"),
    path('form/<str:form_title>/', views.formular, name="form_title"),

    # Django Templatesprache Test
    path('dtl/<int:menu_id>/', views.menu_template_test),
    path('dtl/', views.menu_template_test)
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
