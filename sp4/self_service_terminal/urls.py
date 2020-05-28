from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('menu/<int:menuid>/', views.menu),
    path('form/<int:formid>/', views.formular)
]