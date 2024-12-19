from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.conf import settings
from django.db import models

class PaymentinfoConfig(AppConfig):
    name = 'paymentinfo'

    def ready(self):
        # Delay the model import until after migration
        post_migrate.connect(self.load_paypal_credentials, sender=self)

    def load_paypal_credentials(self, **kwargs):
        # Import models inside the function to avoid the "Apps aren't loaded yet" error
        from paymentinfo.models import PaymentConfig
        try:
            payment_config = PaymentConfig.objects.first()
            if payment_config:
                settings.PAYPAL_CLIENT_ID = payment_config.client_id
                settings.PAYPAL_CLIENT_SECRET = payment_config.client_secret
            else:
                settings.PAYPAL_CLIENT_ID = 'default_client_id'
                settings.PAYPAL_CLIENT_SECRET = 'default_client_secret'
        except PaymentConfig.DoesNotExist:
            settings.PAYPAL_CLIENT_ID = 'default_client_id'
            settings.PAYPAL_CLIENT_SECRET = 'default_client_secret'
