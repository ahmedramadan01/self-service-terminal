# Generated by Django 3.0.6 on 2020-06-11 08:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('self_service_terminal', '0007_auto_20200609_2031'),
    ]

    operations = [
        migrations.AlterField(
            model_name='form',
            name='pdffile',
            field=models.FileField(default='default.pdf', upload_to='forms'),
        ),
    ]
