# Generated by Django 3.0.5 on 2020-06-01 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('self_service_terminal', '0010_merge_20200601_1338'),
    ]

    operations = [
        migrations.AlterField(
            model_name='terminal_settings',
            name='colorval',
            field=models.CharField(blank=True, default='', max_length=7),
        ),
        migrations.AlterField(
            model_name='terminal_settings',
            name='krankenkasse_logo',
            field=models.ImageField(blank=True, default='images/placeholder.jpg', null=True, upload_to='images/'),
        ),
    ]