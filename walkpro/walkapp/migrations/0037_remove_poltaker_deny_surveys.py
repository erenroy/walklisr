# Generated by Django 5.1.2 on 2024-12-18 21:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('walkapp', '0036_poltaker_deny_surveys'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='poltaker',
            name='deny_surveys',
        ),
    ]