# Generated by Django 5.1.2 on 2024-11-08 08:47

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surveyapp', '0014_surveyresponse_polltaker'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='survey_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]