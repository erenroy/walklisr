# Generated by Django 5.1.2 on 2024-11-04 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('walkapp', '0019_generalquestion'),
    ]

    operations = [
        migrations.AddField(
            model_name='poltaker',
            name='Street',
            field=models.IntegerField(default='0', max_length=10),
        ),
        migrations.AddField(
            model_name='poltaker',
            name='city',
            field=models.EmailField(default='0', max_length=10),
        ),
        migrations.AddField(
            model_name='poltaker',
            name='state',
            field=models.CharField(default='0', max_length=10),
        ),
    ]