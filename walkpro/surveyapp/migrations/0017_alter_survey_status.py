# Generated by Django 5.1.2 on 2024-11-08 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surveyapp', '0016_survey_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='survey',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed')], default='pending', max_length=20),
        ),
    ]