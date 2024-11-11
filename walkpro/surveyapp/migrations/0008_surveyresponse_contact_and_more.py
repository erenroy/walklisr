# Generated by Django 5.1.2 on 2024-11-07 08:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surveyapp', '0007_remove_surveyresponse_contact'),
        ('walkapp', '0026_usercontactsearch'),
    ]

    operations = [
        migrations.AddField(
            model_name='surveyresponse',
            name='contact',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='walkapp.usercontactlist'),
        ),
        migrations.AlterField(
            model_name='surveyresponse',
            name='polltaker',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='walkapp.poltaker'),
        ),
        migrations.AlterField(
            model_name='surveyresponse',
            name='survey',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='surveyapp.survey'),
        ),
    ]