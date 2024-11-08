# utils.py

from django.core.mail import send_mail
from django.conf import settings

def send_poltaker_email(poltaker):
    subject = 'Welcome to Our Platform'
    message = f'''
    Hi {poltaker.name},

    Your account has been created successfully. Here are your details:

    Name: {poltaker.name}
    Email: {poltaker.email}
    Zip Code: {poltaker.zip_code}
    Mobile: {poltaker.mobile}
    Password: {poltaker.password}

    You can login using the following link:
    http://your_website_url/login/

    Thank you,
    Your Company Name
    '''

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [poltaker.email],
        fail_silently=False,
    )
