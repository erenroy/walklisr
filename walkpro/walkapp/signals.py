# walkapp/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Question, Option

@receiver(post_save, sender=User)
def create_default_questions(sender, instance, created, **kwargs):
    if created:
        # Create default questions
        q1 = Question.objects.create(
            user=instance,
            question_text="What is your age?",
            question_type="mcq"
        )
        q2 = Question.objects.create(
            user=instance,
            question_text="What is your gender?",
            question_type="mcq"
        )
        q3 = Question.objects.create(
            user=instance,
            question_text="What is your race/ethnicity?",
            question_type="mcq"
        )
        q4 = Question.objects.create(
            user=instance,
            question_text="What is your highest level of education completed?",
            question_type="mcq"
        )
        q5 = Question.objects.create(
            user=instance,
            question_text="What is your current employment status?",
            question_type="mcq"
        )
        q6 = Question.objects.create(
            user=instance,
            question_text="Which political party do you typically support?",
            question_type="mcq"
        )
        q7 = Question.objects.create(
            user=instance,
            question_text="What is your opinion on the current state of the economy?",
            question_type="mcq"
        )
        q8 = Question.objects.create(
            user=instance,
            question_text="How concerned are you about the national debt?",
            question_type="mcq"
        )
        q9 = Question.objects.create(
            user=instance,
            question_text="How important is the issue of healthcare to you?",
            question_type="mcq"
        )
        q10 = Question.objects.create(
            user=instance,
            question_text="Should the government provide universal healthcare?",
            question_type="mcq"
        )
        q11 = Question.objects.create(
            user=instance,
            question_text="What is your opinion on the current immigration policy?",
            question_type="mcq"
        )
        q12 = Question.objects.create(
            user=instance,
            question_text="Should the government provide a path to citizenship for illegal immigrants?",
            question_type="mcq"
        )
        q13 = Question.objects.create(
            user=instance,
            question_text="What is your stance on gun control?",
            question_type="mcq"
        )
        q14 = Question.objects.create(
            user=instance,
            question_text="Should there be limits on the number of guns an individual can own?",
            question_type="mcq"
        )
        q15 = Question.objects.create(
            user=instance,
            question_text="What is your opinion on the death penalty?",
            question_type="mcq"
        )
        q16 = Question.objects.create(
            user=instance,
            question_text="Should abortion be legal?",
            question_type="mcq"
        )
        q17 = Question.objects.create(
            user=instance,
            question_text="What is your opinion on same-sex marriage?",
            question_type="mcq"
        )
        q18 = Question.objects.create(
            user=instance,
            question_text="What is your stance on climate change?",
            question_type="mcq"
        )
        q19 = Question.objects.create(
            user=instance,
            question_text="Should the government invest in renewable energy sources?",
            question_type="mcq"
        )
        q20 = Question.objects.create(
            user=instance,
            question_text="What is your opinion on the Paris Climate Agreement?",
            question_type="mcq"
        )

        # Create default options for the questions
        # Age
        Option.objects.create(question=q1, option_text="18-24")
        Option.objects.create(question=q1, option_text="25-34")
        Option.objects.create(question=q1, option_text="35-44")
        Option.objects.create(question=q1, option_text="45-54")
        Option.objects.create(question=q1, option_text="55-64")
        Option.objects.create(question=q1, option_text="65 or older")

        # Gender
        Option.objects.create(question=q2, option_text="Male")
        Option.objects.create(question=q2, option_text="Female")
        Option.objects.create(question=q2, option_text="Non-binary")
        Option.objects.create(question=q2, option_text="Prefer not to answer")

        # Race/Ethnicity
        Option.objects.create(question=q3, option_text="White")
        Option.objects.create(question=q3, option_text="Black or African American")
        Option.objects.create(question=q3, option_text="Hispanic or Latino")
        Option.objects.create(question=q3, option_text="Asian or Pacific Islander")
        Option.objects.create(question=q3, option_text="American Indian or Alaskan Native")
        Option.objects.create(question=q3, option_text="Other")
        Option.objects.create(question=q3, option_text="Prefer not to answer")

        # Education Level
        Option.objects.create(question=q4, option_text="High school or less")
        Option.objects.create(question=q4, option_text="Some college")
        Option.objects.create(question=q4, option_text="Bachelor’s degree")
        Option.objects.create(question=q4, option_text="Master’s degree or higher")

        # Employment Status
        Option.objects.create(question=q5, option_text="Employed full-time")
        Option.objects.create(question=q5, option_text="Employed part-time")
        Option.objects.create(question=q5, option_text="Unemployed")
        Option.objects.create(question=q5, option_text="Retired")
        Option.objects.create(question=q5, option_text="Student")
        Option.objects.create(question=q5, option_text="Other")

        # Political Party
        Option.objects.create(question=q6, option_text="Democratic Party")
        Option.objects.create(question=q6, option_text="Republican Party")
        Option.objects.create(question=q6, option_text="Libertarian Party")
        Option.objects.create(question=q6, option_text="Green Party")
        Option.objects.create(question=q6, option_text="Independent")
        Option.objects.create(question=q6, option_text="Other")

        # Opinion on Economy
        Option.objects.create(question=q7, option_text="Excellent")
        Option.objects.create(question=q7, option_text="Good")
        Option.objects.create(question=q7, option_text="Fair")
        Option.objects.create(question=q7, option_text="Poor")
        Option.objects.create(question=q7, option_text="Terrible")

        # Concern about National Debt
        Option.objects.create(question=q8, option_text="Very concerned")
        Option.objects.create(question=q8, option_text="Somewhat concerned")
        Option.objects.create(question=q8, option_text="Not very concerned")
        Option.objects.create(question=q8, option_text="Not concerned at all")

        # Importance of Healthcare
        Option.objects.create(question=q9, option_text="Extremely important")
        Option.objects.create(question=q9, option_text="Very important")
        Option.objects.create(question=q9, option_text="Somewhat important")
        Option.objects.create(question=q9, option_text="Not very important")
        Option.objects.create(question=q9, option_text="Not important at all")

        # Universal Healthcare
        Option.objects.create(question=q10, option_text="Yes")
        Option.objects.create(question=q10, option_text="No")
        Option.objects.create(question=q10, option_text="Don’t know")

        # Immigration Policy
        Option.objects.create(question=q11, option_text="Too Strict")
        Option.objects.create(question=q11, option_text="About right")
        Option.objects.create(question=q11, option_text="Too lenient")

        # Path to Citizenship for Immigrants
        Option.objects.create(question=q12, option_text="Yes")
        Option.objects.create(question=q12, option_text="No")
        Option.objects.create(question=q12, option_text="Don’t know")

        # Stance on Gun Control
        Option.objects.create(question=q13, option_text="Support stricter gun control laws")
        Option.objects.create(question=q13, option_text="Support current gun control laws")
        Option.objects.create(question=q13, option_text="Oppose stricter gun control laws")
        Option.objects.create(question=q13, option_text="Don’t know")

        # Gun Ownership Limits
        Option.objects.create(question=q14, option_text="Yes")
        Option.objects.create(question=q14, option_text="No")
        Option.objects.create(question=q14, option_text="Don’t know")

        # Opinion on Death Penalty
        Option.objects.create(question=q15, option_text="Support")
        Option.objects.create(question=q15, option_text="Oppose")
        Option.objects.create(question=q15, option_text="Don’t know")

        # Legalization of Abortion
        Option.objects.create(question=q16, option_text="Yes, in all cases")
        Option.objects.create(question=q16, option_text="Yes, in some cases")
        Option.objects.create(question=q16, option_text="No, in all cases")
        Option.objects.create(question=q16, option_text="Don’t know")

        # Same-Sex Marriage
        Option.objects.create(question=q17, option_text="Support")
        Option.objects.create(question=q17, option_text="Oppose")
        Option.objects.create(question=q17, option_text="Don’t know")

        # Stance on Climate Change
        Option.objects.create(question=q18, option_text="A serious problem that requires immediate action")
        Option.objects.create(question=q18, option_text="A problem that requires action, but not immediately")
        Option.objects.create(question=q18, option_text="A minor problem that does not require immediate action")
        Option.objects.create(question=q18, option_text="Not a problem")

        # Renewable Energy Investment
        Option.objects.create(question=q19, option_text="Yes")
        Option.objects.create(question=q19, option_text="No")
        Option.objects.create(question=q19, option_text="Don’t know")

        # Opinion on Paris Climate Agreement
        Option.objects.create(question=q20, option_text="Support")
        Option.objects.create(question=q20, option_text="Oppose")
        Option.objects.create(question=q20, option_text="Don’t know")