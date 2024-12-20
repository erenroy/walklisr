# Generated by Django 5.1.2 on 2024-12-18 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paymentinfo', '0002_alter_paymentconfig_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentconfig',
            name='payment_method',
            field=models.CharField(choices=[('paypal', 'PayPal'), ('stripe', 'Stripe')], default=1, max_length=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='paymentconfig',
            name='stripe_publishable_key',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='paymentconfig',
            name='stripe_secret_key',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='paymentconfig',
            name='client_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='paymentconfig',
            name='client_secret',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]