# app/admin.py

from django.contrib import admin
from .models import Message

# Registering the Message model to be visible in the admin panel
admin.site.register(Message)
