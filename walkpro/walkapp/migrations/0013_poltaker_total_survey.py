# Generated by Django 5.1.2 on 2024-10-30 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('walkapp', '0012_poltaker_mobile'),
    ]

    operations = [
        migrations.AddField(
            model_name='poltaker',
            name='total_survey',
            field=models.IntegerField(default=0),
        ),
    ]