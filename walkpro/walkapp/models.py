from django.db import models

class PersonData(models.Model):
    PARTY_CHOICES = [
        ('Democrat', 'Democrat'),
        ('Republican', 'Republican'),
        ('Independent', 'Independent'),
    ]

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    party_preference = models.CharField(max_length=20, choices=PARTY_CHOICES)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"



# models.py
from django.db import models
from django.contrib.auth.models import User

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    managers = models.IntegerField(default=0)
    poltakers = models.IntegerField(default=0)
    surveys = models.IntegerField(default=0)
    contacts = models.IntegerField(default=0)

    def __str__(self):
        return self.name

from django.utils import timezone
from datetime import timedelta

class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"

    def is_active(self):
        return self.expiration_date and timezone.now() < self.expiration_date

from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    country = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    street = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)  # Phone number field

    def __str__(self):
        return f"{self.user.username}'s Profile"



# models for user 
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class UserSearch(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    state = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    zip_code = models.CharField(max_length=10, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        # Check if the search is still within the 30-day validity
        return self.created_at >= timezone.now() - timedelta(days=30)

# models.py
from django.db import models
from django.contrib.auth.models import User

class UserContactAccess(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    person = models.ForeignKey(PersonData, on_delete=models.CASCADE)
    accessed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} accessed {self.person.first_name} {self.person.last_name}"

# user SubscriptionPlan details and access list details 

from django.db import models
from django.contrib.auth.models import User

class UserSubscriptionDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    allowed_lives = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - Allowed Lives: {self.allowed_lives}"




# models.py
from django.db import models
from django.contrib.auth.models import User

class Poltaker(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="poltakers")
    name = models.CharField(max_length=100)
    mobile = models.IntegerField(default=0)
    email = models.EmailField(unique=True)
    zip_code = models.CharField(max_length=10)
    password = models.CharField(max_length=128)  # Store hashed password
    # New fields for tracking survey statuses
    completed_surveys = models.IntegerField(default=0)
    inprogress_surveys = models.IntegerField(default=0)
    pending_surveys = models.IntegerField(default=0)
    total_survey = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} (Poltaker for {self.user.username})"



from django.db import models
from django.contrib.auth.models import User

class Question(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=255)

    def __str__(self):
        return self.question_text

class Option(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    option_text = models.CharField(max_length=255)

    def __str__(self):
        return self.option_text


