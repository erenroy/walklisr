# Generated by Django 5.1.2 on 2024-12-18 21:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surveyapp', '0024_remove_survey_denial_reason_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='rejections',
            field=models.BooleanField(default=False),
        ),
    ]
