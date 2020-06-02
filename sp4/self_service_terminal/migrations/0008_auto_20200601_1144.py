# Generated by Django 3.0.5 on 2020-06-01 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('self_service_terminal', '0007_auto_20200529_1615'),
    ]

    operations = [
        migrations.AddField(
            model_name='terminal_settings',
            name='krankenkasse_logo',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
        migrations.AlterField(
            model_name='terminal_settings',
            name='colorval',
            field=models.CharField(max_length=7),
        ),
        migrations.AlterField(
            model_name='terminal_settings',
            name='institute_logo',
            field=models.ImageField(blank=True, default='images/no_logo.jpg', null=True, upload_to='images/'),
        ),
    ]