# Generated by Django 5.1.2 on 2024-10-27 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('walkapp', '0005_remove_userprofile_subscription_plan_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='subscription_plan_name',
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='phone_number',
            field=models.CharField(default=2, max_length=15),
            preserve_default=False,
        ),
    ]