# Generated by Django 5.1.2 on 2024-11-07 09:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('walkapp', '0026_usercontactsearch'),
    ]

    operations = [
        migrations.AddField(
            model_name='usercontactlist',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='usercontactlist',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
