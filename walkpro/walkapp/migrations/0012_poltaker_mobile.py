# Generated by Django 5.1.2 on 2024-10-30 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('walkapp', '0011_poltaker_completed_surveys_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='poltaker',
            name='mobile',
            field=models.IntegerField(default=0),
        ),
    ]
