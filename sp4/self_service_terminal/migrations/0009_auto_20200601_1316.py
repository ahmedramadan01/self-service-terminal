# Generated by Django 3.0.5 on 2020-06-01 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('self_service_terminal', '0008_auto_20200601_1144'),
    ]

    operations = [
        migrations.AlterField(
            model_name='terminal_settings',
            name='colorval',
            field=models.CharField(blank=True, default='', max_length=7),
        ),
        migrations.AlterField(
            model_name='terminal_settings',
            name='institute_logo',
            field=models.ImageField(blank=True, default='images/placeholder.jpg', null=True, upload_to='images/'),
        ),
    ]