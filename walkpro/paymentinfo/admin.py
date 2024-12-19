from django.contrib import admin
from .models import PaymentConfig

@admin.register(PaymentConfig)
class PaymentConfigAdmin(admin.ModelAdmin):
    list_display = ('payment_method', 'client_id', 'stripe_publishable_key')
    list_filter = ('payment_method',)
    search_fields = ('payment_method',)
