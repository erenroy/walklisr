# Generated by Django 5.1.2 on 2024-11-07 15:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('surveyapp', '0012_alter_surveyresponse_polltaker'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='surveyresponse',
            name='polltaker',
        ),
    ]
