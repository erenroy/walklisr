# app/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('contactsms/', views.contact_view, name='contact_view'),  # URL for form submission
]
