from django.db import models

class Form(models.Model):
    upload_date = models.DateTimeField()
    last_changed = models.DateTimeField()
    show_on_frontend = models.BooleanField()
    description = models.CharField(max_length=120)