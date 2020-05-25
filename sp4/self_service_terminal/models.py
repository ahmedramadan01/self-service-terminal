import datetime

from django.db import models
from django.utils import timezone

class Design(models.Model):
    """Store the settings for color and logos"""
    # TODO set max value for valid hex color values
    colorval = models.PositiveIntegerField(null=True, blank=True)
    institute_logo = models.ImageField(upload_to='images', null=True, blank=True)

    class Meta:
        abstract = True

class Homepage(Design):
    """Model the homepage of the self service terminal"""
    start_title = models.CharField(max_length=100)
    start_text = models.TextField()

    def __str__(self):
        return self.start_title
    

class Menu(models.Model):
    """Model the menus and submenus of the self service terminal"""
    homepage = models.ForeignKey(Homepage, on_delete=models.CASCADE)
    parent_menu = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    menu_title = models.CharField(max_length=100)
    menu_text = models.TextField(blank=True)

    def __str__(self):
        return self.menu_title

class Form(models.Model):
    """Model the forms to be accessed via the self service terminal"""
    parent_menu = models.ForeignKey('Menu', on_delete=models.CASCADE, blank=True, null=True)
    pdffile = models.FileField(upload_to='forms', null=True, blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    last_changed = models.DateTimeField(auto_now=True)
    show_on_frontend = models.BooleanField(default=False)
    form_title = models.CharField(max_length=120, default="Formular")
    description = models.TextField(blank=True)

    # TODO printing method
    def print_form(self):
        """ Print the document using the cups software."""
        pass

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