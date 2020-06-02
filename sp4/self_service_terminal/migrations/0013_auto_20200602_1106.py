# Generated by Django 3.0.5 on 2020-06-02 09:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('self_service_terminal', '0012_auto_20200602_1043'),
    ]

    operations = [
        migrations.AlterField(
            model_name='terminal_settings',
            name='institute_logo',
            field=models.ImageField(blank=True, default='static/Tu-ilmenauLogo.png', upload_to='images'),
        ),
        migrations.AlterField(
            model_name='terminal_settings',
            name='krankenkasse_logo',
            field=models.ImageField(blank=True, default='static/Logo_AOK_PLUS.svg.png', upload_to='images'),
        ),
    ]
