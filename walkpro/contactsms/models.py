# app/models.py

from django.db import models

class Message(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return f"Message from {self.full_name} ({self.email})"
