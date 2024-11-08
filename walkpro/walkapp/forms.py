# forms.py

from django import forms

class SubscriptionForm(forms.Form):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField()
    country = forms.CharField(max_length=50)
    city = forms.CharField(max_length=50)
    zip_code = forms.CharField(max_length=10)
