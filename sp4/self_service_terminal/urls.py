from django.urls import path

from . import views

# TODO Use custom path converters?
# https://docs.djangoproject.com/en/3.0/topics/http/urls/#registering-custom-path-converters

urlpatterns = [
    path('', views.index, name='index'),
    path('menu/<int:menu_id>/', views.menu),
    path('menu/<str:menu_title>/', views.menu),
    path('form/<int:form_id>/', views.formular),
    path('form/<str:form_title>/', views.formular)
]