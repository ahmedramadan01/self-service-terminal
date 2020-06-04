import datetime
import os
import subprocess

from django.db import models
from django.utils import timezone


from .constants import *


class Terminal_Settings(models.Model):
    """Model the settings of the self service terminal."""
    title = models.CharField(max_length=TITLE_LENGTH)
    description = models.TextField()
    homepage = models.OneToOneField(
        'Menu', on_delete=models.CASCADE, blank=True, null=True)
    colorval_nav_bar = models.CharField(max_length=7, blank=True, default='')
    colorval_heading = models.CharField(max_length=7, blank=True, default='')
    colorval_text = models.CharField(max_length=7, blank=True, default='')
    colorval_button = models.CharField(max_length=7, blank=True, default='')
    colorval_zurueck_button = models.CharField(
        max_length=7, blank=True, default='')
    institute_logo = models.ImageField(
        upload_to='images', default='static/Tu-ilmenauLogo.png', blank=True)
    krankenkasse_logo = models.ImageField(
        upload_to='images', default='static/Logo_AOK_PLUS.svg.png', blank=True)

    def __str__(self):
        return self.title


class Menu(models.Model):
    """Model the menus and submenus of the self service terminal."""
    settings = models.ForeignKey(Terminal_Settings, on_delete=models.CASCADE)
    parent_menu = models.ForeignKey(
        'self', on_delete=models.CASCADE, blank=True, null=True)
    menu_title = models.CharField(max_length=TITLE_LENGTH)
    menu_text = models.TextField(blank=True)

    def __str__(self):
        return self.menu_title


class Form(models.Model):
    """Model the forms to be accessed via the self service terminal."""
    parent_menu = models.ForeignKey('Menu', on_delete=models.CASCADE)
    pdffile = models.FileField(upload_to='forms', null=True, blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    last_changed = models.DateTimeField(auto_now=True)
    show_on_frontend = models.BooleanField(default=False)
    form_title = models.CharField(max_length=TITLE_LENGTH, default="Formular")
    description = models.TextField(blank=True)

    # TODO printing method
    def print_form(self, number_of_copies=1):
        """ Print the document using the linux command lpr."""
        args = ['lpr', self.pdffile.path]
        result = subprocess.run(args, capture_output=True)
        if result.returncode:
            print('Error: Print command has not been executed.')
        else:
            print('Print', self.pdffile.name)

    def time_since_last_updated(self):
        """Return a tuple in the form (days, hours, minutes)."""
        delta = timezone.now() - self.last_changed
        days = delta.days
        hours = int((delta.seconds / 60) / 60)
        minutes = int((delta.seconds) / 60) - hours * 60
        return (days, hours, minutes)

    def time_since_last_updated_str(self):
        """Return a string in german with days, hours, minutes since last updated."""
        (days, hours, minutes) = self.time_since_last_updated()
        return "Zuletzt geändert vor " + str(days) + " Tagen, " + str(hours) + " Stunden, " + str(minutes) + " Minuten."

    def __str__(self):
        return self.form_title
