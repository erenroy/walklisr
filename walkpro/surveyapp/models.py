# surveyapp/models.py

from django.db import models
from django.contrib.auth.models import User
from walkapp.models import Poltaker  # Assuming Poltaker model is in walkapp
from walkapp.models import Question  # Assuming Question model is in walkapp
from walkapp.models import UserContactList
from django.utils import timezone
class Survey(models.Model):
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='surveys')
    polltaker = models.ForeignKey(Poltaker, on_delete=models.CASCADE, related_name="surveys")
    questions = models.ManyToManyField(Question, related_name="surveys")
    contacts = models.ManyToManyField(UserContactList, related_name='surveys')  # Add this line
    created_at = models.DateTimeField(auto_now_add=True)
    survey_date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed')], default='pending')

    def update_polltaker_counts(self):
        """Update the Poltaker's counts based on the current status of the Survey."""
        polltaker = self.polltaker

        # Decrement previous status count
        if self.status == 'completed':
            polltaker.completed_surveys += 1
            if polltaker.pending_surveys > 0:  # Decrease from pending only if there's any pending
                polltaker.pending_surveys -= 1
        elif self.status == 'in_progress':
            polltaker.inprogress_surveys += 1
            if polltaker.pending_surveys > 0:
                polltaker.pending_surveys -= 1
        elif self.status == 'pending':
            polltaker.pending_surveys += 1
            if polltaker.inprogress_surveys > 0:
                polltaker.inprogress_surveys -= 1

        # Recalculate the total surveys count
        polltaker.total_survey = polltaker.completed_surveys + polltaker.inprogress_surveys + polltaker.pending_surveys
        polltaker.save()

    def save(self, *args, **kwargs):
        """Override save method to check for status change and update counts."""
        if self.pk:  # If the object already exists (not a new one)
            old_status = Survey.objects.get(pk=self.pk).status
            if old_status != self.status:  # Only update if status is changing
                self.update_polltaker_counts()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def __str__(self):
        return self.title

class SurveyResponse(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    polltaker = models.ForeignKey(Poltaker, on_delete=models.CASCADE)
    contact = models.ForeignKey(UserContactList, on_delete=models.CASCADE, null=True)
    responses = models.JSONField()  # Store responses as JSON
    submitted_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=True)  # New field to mark completion

    def __str__(self):
        return f"Response by {self.polltaker} for survey '{self.survey.title}'"

