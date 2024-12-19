from django.db import models

class PaymentConfig(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe'),
    )
    
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    client_id = models.CharField(max_length=255, blank=True, null=True)  # For PayPal
    client_secret = models.CharField(max_length=255, blank=True, null=True)  # For PayPal
    stripe_publishable_key = models.CharField(max_length=255, blank=True, null=True)  # For Stripe
    stripe_secret_key = models.CharField(max_length=255, blank=True, null=True)  # For Stripe
    
    def __str__(self):
        return f"Payment Config ({self.payment_method})"
