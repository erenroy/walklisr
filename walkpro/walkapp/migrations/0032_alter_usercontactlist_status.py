# Generated by Django 5.1.2 on 2024-11-11 07:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('walkapp', '0031_usercontactlist_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usercontactlist',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('denied', 'Denied')], max_length=50),
        ),
    ]