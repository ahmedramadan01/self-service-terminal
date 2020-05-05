from django.db import models

class Form(models.Model):
    upload_date = models.DateTimeField()
    last_changed = models.DateTimeField()
    show_on_frontend = models.BooleanField()
    description = models.CharField(max_length=120)

    def __str__(self):
        return self.description

class Which_year(models.Model):
    form = models.ForeignKey(Form,on_delete = models.CASCADE)
    which_year_text = models.CharField(max_length=4)