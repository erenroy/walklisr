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
    # password = models.CharField(max_length=128)  # Store hashed password
    Street = models.CharField(max_length=10,default='0')
    city = models.CharField(max_length=10,default='0')
    state = models.CharField(max_length=10,default='0')
    password = models.CharField(max_length=128)  # Store hashed password
    # New fields for tracking survey statuses
    completed_surveys = models.IntegerField(default=0)
    inprogress_surveys = models.IntegerField(default=0)
    pending_surveys = models.IntegerField(default=0)
    total_survey = models.IntegerField(default=0)
    password_changed = models.BooleanField(default=False)  # Add this field
    password_reset_token = models.CharField(max_length=256, null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} (Poltaker for {self.user.username})"



from django.db import models
from django.contrib.auth.models import User

class Question(models.Model):
    QUESTION_TYPES = (
        ('mcq', 'Multiple Choice'),
        ('text', 'Open Text'),
        ('yesno', 'Yes/No'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=255)
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES)
    
    
    def __str__(self):
        return self.question_text

class Option(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    option_text = models.CharField(max_length=255)

    def __str__(self):
        return self.option_text



# models.py
from django.db import models
from django.contrib.auth.models import User
import uuid

class PasswordReset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reset_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_when = models.DateTimeField(auto_now_add=True)


from django.db import models

class GeneralQuestion(models.Model):
    QUESTION_TYPES = [
        ('mcq', 'Multiple Choice'),
        ('text', 'Open Text'),
        ('yesno', 'Yes/No'),
    ]

    question_text = models.CharField(max_length=255)
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES)
    options = models.TextField(blank=True)  # Store options as newline-separated values

    def __str__(self):
        return self.question_text

# Addding contact listsz 
from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User

# class UserContactList(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     first_name = models.CharField(max_length=100)
#     last_name = models.CharField(max_length=100)
#     email = models.EmailField()
#     street = models.CharField(max_length=255)
#     city = models.CharField(max_length=100)
#     state = models.CharField(max_length=100)
#     country = models.CharField(max_length=100)
#     zipcode = models.PositiveIntegerField()  # Ensure this matches the HTML form
#     latitude = models.FloatField(null=True, blank=True)
#     longitude = models.FloatField(null=True, blank=True)
#     party_preference = models.CharField(max_length=50, choices=[
#         ('Republican', 'Republican'),
#         ('Democrat', 'Democrat'),
#         ('Independent', 'Independent'),
#     ])

#     def __str__(self):
#         return f"{self.first_name} {self.last_name} - {self.email}"

class UserContactSearch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    pct_nbr = models.CharField(max_length=100, null=True, blank=True)
    district = models.CharField(max_length=100, null=True, blank=True)
    ward = models.CharField(max_length=100, null=True, blank=True)
    zipcode = models.CharField(max_length=20, null=True, blank=True)
    search_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.search_date}"


# next trail 
from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User

class UserContactList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    street = models.CharField(max_length=255, blank=True, default='NA')
    city = models.CharField(max_length=100, blank=True, default='NA')
    state = models.CharField(max_length=100, blank=True, default='NA')
    country = models.CharField(max_length=100, blank=True, default='NA')
    zipcode = models.CharField(max_length=20, blank=True, default='NA')  # Updated to CharField
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    party_preference = models.CharField(max_length=50, choices=[
        ('Republican', 'Republican'),
        ('Democrat', 'Democrat'),
        ('Independent', 'Independent'),
        ('NA', 'NA'),  # Added 'NA' as a choice
    ], blank=True, default='NA')

    # New fields added with `null=True` and `blank=True`
    state_id = models.CharField(max_length=50, null=True, blank=True, default='NA')
    voter_nbr = models.CharField(max_length=50, null=True, blank=True, default='NA')
    title = models.CharField(max_length=50, null=True, blank=True, default='NA')
    address = models.CharField(max_length=255, null=True, blank=True, default='NA')
    address2 = models.CharField(max_length=255, null=True, blank=True, default='NA')
    phone = models.CharField(max_length=15, null=True, blank=True, default='NA')
    dob = models.DateField(null=True, blank=True)
    reg_date = models.DateField(null=True, blank=True)
    district = models.CharField(max_length=50, null=True, blank=True, default='NA')
    pct_nbr = models.CharField(max_length=50, null=True, blank=True, default='NA')
    ward = models.CharField(max_length=50, null=True, blank=True, default='NA')
    # New 'status' field added
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('completed', 'Completed'), ('denied', 'Denied')],default='pending' )
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"


