# Generated by Django 5.1.2 on 2024-11-24 12:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('walkapp', '0033_alter_usercontactlist_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='usercontactsearch',
            name='district',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='usercontactsearch',
            name='precinct_number',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='usercontactsearch',
            name='ward',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='usercontactsearch',
            name='zipcode',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
