import datetime
import os
import subprocess

from django.db import models
from django.utils import timezone

from .constants import *


class Terminal_Settings(models.Model):
    """Model the settings of the self service terminal.

    Contains settings fields for the colors and logos of the user interface.
    Values must be valid for CSS. Example: #aabbcc or black
    Sets the homepage menu.
    Title and description fields are deprecated.

    Important: Currently only the Terminal_Settings instance with the
    title='settings' is used in the Self service terminal.
    """
    title = models.CharField(max_length=TITLE_LENGTH, unique=True,
        verbose_name='Titel')
    description = models.TextField(blank=True, null=True,
        verbose_name='Beschreibung')

    colorval_nav_bar = models.CharField(max_length=7, blank=True, default='',
        verbose_name='Farbe der Kopfleiste')
    colorval_heading = models.CharField(max_length=7, blank=True, default='',
        verbose_name='Farbe der Überschriften')
    colorval_text = models.CharField(max_length=7, blank=True, default='',
        verbose_name='Farbe der Texte')
    colorval_button = models.CharField(max_length=7, blank=True, default='',
        verbose_name='Farbe der Buttons')
    colorval_return_button = models.CharField(max_length=7, blank=True,
        default='', verbose_name='Farbe des Zurück-Buttons')
    institute_logo = models.ImageField(
        upload_to='images', default='images/institute_logo.png',
        verbose_name='Institutslogo')
    insurance_logo = models.ImageField(
        upload_to='images', default='images/insurance_logo.png',
        verbose_name='Krankenkassenlogo')

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Einstellungen'
        verbose_name_plural = 'Einstellungen'

class Menu(models.Model):
    """Model the menus and submenus of the self service terminal.

    Is linked to its parent menu via a ForeignKey Field. Contains only its
    title and some descriptive text.
    """
    parent_menu = models.ForeignKey('self', on_delete=models.CASCADE,
        blank=True, null=True, verbose_name='Eltern-Menü')
    menu_title = models.CharField(max_length=TITLE_LENGTH,
        verbose_name='Titel')
    menu_text = models.TextField(blank=True, verbose_name='Beschreibung')

    def __str__(self):
        return self.menu_title

    class Meta:
        verbose_name = 'Menü'
        verbose_name_plural = 'Menüs'


class Form(models.Model):
    """Model the forms to be accessed via the self service terminal.

    Is linked to its parent menu via a ForeignKey Field. Contains a File
    Field for the PDF forms it will hold. Has some info about its upload date
    and last change. Has a title and some descriptive text.
    """
    parent_menu = models.ForeignKey('Menu', on_delete=models.CASCADE,
        verbose_name='Eltern-Menü')
    pdffile = models.FileField(upload_to='forms', default="forms/default.pdf",
        verbose_name='PDF-Datei')
    upload_date = models.DateTimeField(auto_now_add=True,
        verbose_name='Uploaddatum')
    last_changed = models.DateTimeField(auto_now=True,
        verbose_name='Zuletzt geändert')
    show_on_frontend = models.BooleanField(default=False,
        verbose_name='Im Frontend anzeigen')
    form_title = models.CharField(max_length=TITLE_LENGTH, default="Formular",
        verbose_name='Titel')
    description = models.TextField(blank=True, verbose_name='Beschreibung')

    def print_form(self, number_of_copies=1):
        """ Print the document.

        Print the pdffile. The command is passed to the Linux operating system
        using the Python STL module subprocess. If the command run() runs
        successfully and returns 1, return True, else return False and issue
        an error message. The contents of stderr is printed on stdout.
        """
        args = ['lp', self.pdffile.path]
        result = subprocess.run(args, capture_output=True)
        if result.returncode:
            print('Error: "lp ' + self.pdffile.name + '" returned 1.')
            print(result.stderr)
            return False
        else:
            print('Printing', self.pdffile.name)
            return True

    def time_since_last_updated(self):
        """Return the time passed since the form was updated.

        Return a tuple in the form (days, hours, minutes)."""
        delta = timezone.now() - self.last_changed
        days = delta.days
        hours = int((delta.seconds / 60) / 60)
        minutes = int((delta.seconds) / 60) - hours * 60
        return (days, hours, minutes)

    def time_since_last_updated_str(self):
        """Return a string in german with days, hours, minutes since last updated."""
        (days, hours, minutes) = self.time_since_last_updated()
        return "Zuletzt geändert vor " + \
            str(days) + " Tagen, " + str(hours) + \
            " Stunden, " + str(minutes) + " Minuten."
    # To change name on admin site
    time_since_last_updated_str.short_description = 'Zeit seit letzter Änderung'

    def __str__(self):
        return self.form_title

    class Meta:
        verbose_name = 'Formular'
        verbose_name_plural = 'Formulare'