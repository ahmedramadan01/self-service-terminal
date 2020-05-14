from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('years/',views.years, name='years'),
    path('formular/',views.formular, name='formular'),
    path('years/formular/',views.formular, name='years/formular/')
]