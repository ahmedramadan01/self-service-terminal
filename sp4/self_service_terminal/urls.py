from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('formular/',views.formular, name='formular')
]