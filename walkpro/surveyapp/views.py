# surveyapp/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Survey
from walkapp.models import GeneralQuestion, Poltaker

# @login_required
# def create_survey(request):
#     """
#     Allows a user to create a survey, select questions, and assign it to a polltaker.
#     """
#     if request.method == 'POST':
#         # Retrieve data from POST request
#         title = request.POST.get('title')
#         description = request.POST.get('description')
#         question_ids = request.POST.getlist('questions')  # Selected question IDs
#         polltaker_id = request.POST.get('polltaker')  # Selected polltaker ID

#         # Create a new survey instance
#         survey = Survey.objects.create(
#             title=title,
#             description=description,
#             created_by=request.user,
#             polltaker_id=polltaker_id
#         )

#         # Assign selected questions to the survey
#         questions = GeneralQuestion.objects.filter(id__in=question_ids)
#         survey.questions.set(questions)

#         return redirect('surveyapp:polltaker_surveys')  # Redirect to polltaker's survey list page

#     # If GET request, display available questions and polltakers
#     questions = GeneralQuestion.objects.all()
#     polltakers = Poltaker.objects.all()
#     return render(request, 'surveyapp/create_survey.html', {
#         'questions': questions,
#         'polltakers': polltakers
#     })


@login_required
def polltaker_surveys(request):
    """
    Displays the surveys assigned to the logged-in polltaker.
    """
    try:
        polltaker = request.user.poltakers.first()  # Assuming each user has one polltaker profile
        surveys = Survey.objects.filter(polltaker=polltaker)
    except Poltaker.DoesNotExist:
        surveys = None

    return render(request, 'surveyapp/polltaker_surveys.html', {'surveys': surveys})



from django.shortcuts import render, redirect
from django.contrib import messages
from walkapp.models import Poltaker  # Import Poltaker from walkapp

# Poltaker Login View
from django.contrib import messages
from django.shortcuts import render, redirect
from walkapp.models import Poltaker
# surveyapp/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from walkapp.models import Poltaker  # Import from walkapp

def poltaker_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            # Fetch the Poltaker by email
            poltaker = Poltaker.objects.get(email=email)

            # Check if the entered password matches (no hashing, plain text)
            if poltaker.password == password:  # Direct comparison with plain text
                # Set session for the logged-in Poltaker
                request.session['poltaker_id'] = poltaker.id

                # Check if password_changed is False
                if not poltaker.password_changed:
                    return redirect('surveyapp:password_change')  # Redirect to the password change page

                return redirect('surveyapp:poltaker_dashboard')  # Redirect to the dashboard if password has been changed
            else:
                messages.error(request, 'Invalid password. Please try again.')
        except Poltaker.DoesNotExist:
            messages.error(request, 'Poltaker with this email does not exist.')

    return render(request, 'poltaker/login.html')

def password_change(request):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password == confirm_password:
            # Get the Poltaker from the session
            poltaker_id = request.session.get('poltaker_id')
            if poltaker_id:
                poltaker = Poltaker.objects.get(id=poltaker_id)
                # Update the password directly (plain text)
                poltaker.password = new_password
                poltaker.password_changed = True  # Update the password_changed field
                poltaker.save()  # Save the Poltaker object

                # Redirect to the dashboard or login page after updating the password
                messages.success(request, 'Password successfully changed.')
                return redirect('surveyapp:poltaker_dashboard')
        else:
            messages.error(request, 'Passwords do not match.')

    return render(request, 'poltaker/password.html')
# View to display forgot password form
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.conf import settings
from walkapp.models import Poltaker  # Import the Poltaker model from walkapp
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            poltaker = Poltaker.objects.get(email=email)
            
            # Generate a token for the password reset process
            token = get_random_string(length=32)  # You could also use Django's default token generator

            # Create a password reset link (use urlsafe_base64_encode for safety)
            reset_link = f"{request.build_absolute_uri('/surveyapp/reset-password/')}?token={token}"

            # Send reset link to the poltaker's email
            send_mail(
                'Password Reset Request',
                f'Hello {poltaker.name},\n\nClick the link below to reset your password:\n\n{reset_link}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
            )

            # Store the token temporarily (this can be saved in the database for further validation)
            poltaker.password_reset_token = token  # Optional: add a field to the Poltaker model to store the token
            poltaker.save()

            messages.success(request, 'A password reset link has been sent to your email.')
            return redirect('surveyapp:poltaker_login')

        except Poltaker.DoesNotExist:
            messages.error(request, 'Poltaker with this email does not exist.')
    
    return render(request, 'poltaker/forget_password.html')

# View to handle reset password
def reset_password(request):
    token = request.GET.get('token')  # Get the token from the URL
    
    # Fetch the Poltaker by the password reset token
    poltaker = Poltaker.objects.filter(password_reset_token=token).first()

    if not poltaker:
        messages.error(request, "Invalid or expired token.")
        return redirect('surveyapp:forgot_password')  # Redirect to forgot password page if token is invalid

    if request.method == 'POST':
        # Get the new password from the form
        new_password = request.POST.get('password')  # This is where the form data comes in
        
        if new_password:
            # Save the password as entered (no hashing)
            poltaker.password = new_password  # Store the password as plain text

            # Optionally clear the reset token if you want to ensure it can only be used once
            poltaker.password_reset_token = None  # Clear the reset token

            # Save the Poltaker object with the updated password
            poltaker.save()

            messages.success(request, "Your password has been reset successfully.")
            return redirect('surveyapp:poltaker_login')  # Redirect to login page after reset
        else:
            messages.error(request, "Password cannot be empty.")  # Error message if password is empty

    return render(request, 'poltaker/reset_password.html', {'poltaker': poltaker})

# surveyapp/views.py

# def poltaker_dashboard(request):
#     # Ensure that the Poltaker is logged in
#     if 'poltaker_id' not in request.session:
#         return redirect('surveyapp:poltaker_login')  # Redirect to login if not authenticated

#     # Retrieve the logged-in Poltaker using the session data
#     poltaker = Poltaker.objects.get(id=request.session['poltaker_id'])

#     # Get only surveys assigned to this Poltaker
#     assigned_surveys = Survey.objects.filter(polltaker=poltaker)

#     # Pass the surveys and Poltaker info to the template
#     context = {
#         'poltaker': poltaker,
#         'surveys': assigned_surveys
#     }
#     return render(request, 'poltaker/dashboard.html', context)

# Poltaker Logout View
def poltaker_logout(request):
    # Clear session data to log out the Poltaker
    request.session.flush()
    return redirect('first_look')




# logic for survey -------------------------------------------------------------------
# surveyapp/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from walkapp.models import Question, Poltaker
from .models import Survey
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Survey
from walkapp.models import Poltaker, Question
from walkapp.models import GeneralQuestion

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from .models import Survey
from walkapp.models import Poltaker, Question, GeneralQuestion
from walkapp.models import Option

from walkapp.models import UserContactList
from django.contrib import messages
from django.shortcuts import render, redirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from walkapp.models import UserContactList, UserSubscription

import random
import string
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
@login_required

def create_survey(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        polltaker_ids = request.POST.getlist('polltaker')  # Allow multiple polltakers
        contact_ids = request.POST.getlist('contacts')  # Get the selected contacts

        # Retrieve the survey date from the form, default to today if not provided
        survey_date = request.POST.get('survey_date')
        if not survey_date:
            survey_date = timezone.now().date()  # Default to today's date
        else:
            survey_date = timezone.datetime.strptime(survey_date, '%Y-%m-%d').date()  # Parse input date

        # Validate and retrieve selected Polltakers
        polltakers = []
        for polltaker_id in polltaker_ids:
            try:
                polltaker = Poltaker.objects.get(id=polltaker_id, user=request.user)
                polltakers.append(polltaker)
            except Poltaker.DoesNotExist:
                messages.error(request, "Invalid Polltaker selection.")
                return redirect('surveyapp:create_survey')

        # Validate and retrieve selected Contacts
        contacts = []
        for contact_id in contact_ids:
            try:
                contact = UserContactList.objects.get(id=contact_id, user=request.user)
                contacts.append(contact)
            except UserContactList.DoesNotExist:
                messages.error(request, "Invalid Contact selection.")
                return redirect('surveyapp:create_survey')

        # Collect selected questions from both models
        question_ids = request.POST.getlist('questions')
        custom_questions_texts = request.POST.getlist('custom_question_text')
        custom_questions_types = request.POST.getlist('custom_question_type')
        custom_mcq_options = request.POST.getlist('mcq_options[]')  # For MCQ options input

        # Generate a unique 10 to 15 digit token for the group of surveys
        def generate_unique_token():
            characters = string.ascii_letters + string.digits
            token = ''.join(random.choice(characters) for _ in range(random.randint(10, 15)))  # Random length of 10 to 15
            return token

        # Generate the token once for the group of surveys (same token for all)
        survey_token = generate_unique_token()

        # Loop through the contacts and create a survey for each one
        for contact in contacts:
            # Update the contact's status to 'pending'
            contact.status = 'pending'
            contact.save()

            for polltaker in polltakers:
                # Create the survey for the current contact
                survey = Survey.objects.create(
                    title=title,
                    description=description,
                    created_by=request.user,
                    polltaker=polltaker,
                    survey_date=survey_date,  # Save the selected date
                    survey_token=survey_token,  # Use the same token for all surveys in this group
                )

                # Set selected questions from existing questions
                survey.questions.set(Question.objects.filter(id__in=question_ids, user=request.user))

                # Adding custom questions to survey
                for i, question_text in enumerate(custom_questions_texts):
                    question_type = custom_questions_types[i]
                    if question_text.strip():
                        # Create the custom question
                        # Create the custom question only if it doesn't already exist
                        if not Question.objects.filter(
                            question_text=question_text,
                            question_type=question_type,
                            user=request.user
                        ).exists():
                            question = Question.objects.create(
                            question_text=question_text,
                            question_type=question_type,
                            user=request.user
                        )
                        else:
                            print("Question already exists. Skipping creation.")
                        # If it's an MCQ, handle the options
                        if question_type == 'mcq' and custom_mcq_options:
                            options = custom_mcq_options[i].split(',')
                            for option_text in options:
                                Option.objects.create(
                                    question=question,
                                    option_text=option_text.strip()
                                )

                        # Add the custom question to the survey
                        survey.questions.add(question)

                # Add the current contact to the survey
                survey.contacts.add(contact)

        messages.success(request, 'Surveys created and assigned to selected Polltakers and Contacts.')
        return redirect('surveyapp:create_survey')

    # For rendering the form
    user_subscription = get_object_or_404(UserSubscription, user=request.user)
    contacts_limit = user_subscription.plan.contacts  # Ensure this attribute exists

    # Fetch questions and contacts
    questions = Question.objects.filter(user=request.user)
    poltakers = Poltaker.objects.filter(user=request.user)
    contacts = UserContactList.objects.filter(user=request.user)[:contacts_limit]
    username = request.user.username if request.user.is_authenticated else None

    context = {
        'questions': questions,
        'poltakers': poltakers,
        'contacts': contacts,
        'username': username,
    }
    return render(request, 'poltaker/create_survey.html', context)
# surveyapp/views.py
# surveyapp/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Survey, SurveyResponse
from walkapp.models import Poltaker, Question
from django.contrib import messages

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Survey, SurveyResponse, Poltaker, UserContactList


# def submit_survey(request, survey_id):
#     survey = Survey.objects.get(id=survey_id)

#     # Ensure that the `polltaker` is fetched from the session or context, not the user directly
#     try:
#         polltaker = Poltaker.objects.get(id=request.session['poltaker_id'])  # Assuming you have `poltaker_id` stored in the session
#     except Poltaker.DoesNotExist:
#         messages.error(request, 'Polltaker record not found.')
#         return redirect('survey_list')

#     # Contact can be any associated with the `polltaker`, modify as needed
#     contact = UserContactList.objects.filter(user=polltaker.user).first()

#     if request.method == 'POST':
#         responses = {}

#         # Loop through each question and get the answer
#         for question in survey.questions.all():
#             answer = request.POST.get(f"question_{question.id}")
#             if question.question_type in ['mcq', 'yesno']:
#                 responses[question.question_text] = answer
#             elif question.question_type == 'text':
#                 responses[question.question_text] = answer

#         # Create the SurveyResponse entry with the contact info
#         SurveyResponse.objects.create(
#             survey=survey,
#             polltaker=polltaker,  # Ensure this is based on the current `polltaker`
#             contact=contact,
#             responses=responses
#         )

#         messages.success(request, 'Survey submitted successfully!')
#         return redirect('survey_list')  # Redirect to the survey list or another page

#     context = {'survey': survey}
#     return render(request, 'surveyapp/take_survey.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from .models import Survey, SurveyResponse
from walkapp.models import Question
from django.contrib.auth.decorators import login_required

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .models import Survey, SurveyResponse
from walkapp.models import Question, GeneralQuestion  # Import GeneralQuestion

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Survey, SurveyResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Survey, SurveyResponse, UserContactList
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Survey,  SurveyResponse
from walkapp.models import Poltaker
# Ensure the view is dependent only on Poltaker login
def take_survey(request, survey_id):
    # Get the survey or return a 404 if it doesn't exist
    survey = get_object_or_404(Survey, id=survey_id)

    # Fetch the Poltaker from the session to ensure they are logged in
    poltaker_id = request.session.get('poltaker_id')
    if not poltaker_id:
        return redirect('surveyapp:poltaker_login')  # Redirect to login if Poltaker isn't logged in

    try:
        poltaker = Poltaker.objects.get(id=poltaker_id)
    except Poltaker.DoesNotExist:
        return redirect('surveyapp:poltaker_login')  # Redirect if Poltaker isn't found

    # Check if the poltaker is authorized to take this survey
    if survey.polltaker and poltaker != survey.polltaker:
        return redirect('surveyapp:poltaker_dashboard')  # Redirect if the Poltaker is unauthorized

    # Fetch the contacts related to this survey
    contacts = survey.contacts.all()

    # Create a dictionary to hold detailed contact information (optional)
    contact_details = {}
    for contact in contacts:
        user_contact = UserContactList.objects.filter(user=contact.user).first()
        if user_contact:
            contact_details[contact.id] = user_contact  # Store the contact information

    # Automatically assign the first contact or customize this logic if necessary
    assigned_contact = contacts.first()

    if request.method == 'POST':
        responses_data = {}

        # Loop through each question to collect answers
        for question in survey.questions.all():
            answer_text = request.POST.get(f'answer_{question.id}', '')
            selected_option = request.POST.get(f'option_{question.id}', '')

            # Save responses based on question type
            if question.question_type == 'mcq' and selected_option:
                responses_data[question.question_text] = {'selected_option': selected_option}
            elif question.question_type == 'text' and answer_text:
                responses_data[question.question_text] = {'answer_text': answer_text}
            elif question.question_type == 'yesno' and answer_text:
                responses_data[question.question_text] = {'answer_text': answer_text}

        # Create a SurveyResponse with the data collected
        SurveyResponse.objects.create(
            survey=survey,
            polltaker=poltaker,  # The current logged-in Poltaker
            contact=assigned_contact,  # The assigned contact
            responses=responses_data,
        )

        # Show success message and redirect
        messages.success(request, 'Survey submitted successfully!')
        # return redirect('surveyapp:poltaker_dashboard')  # Redirect after submission
        # return redirect('surveyapp:all_token_survey', survey_token=survey.survey_token)
        # Check if there are any surveys with the token and valid contacts
        surveys = Survey.objects.filter(
            survey_token=survey.survey_token,
            polltaker=poltaker
        ).annotate(
            valid_contacts=Count('contacts', filter=~Q(contacts__status__in=['completed', 'denied']))
        ).filter(valid_contacts__gt=0)

        # If no valid surveys, redirect to the dashboard
        if not surveys.exists():
            return redirect('surveyapp:poltaker_dashboard')  # Redirect to dashboard if no valid surveys

        # Redirect to the all_token_survey page with the survey_token
        return redirect('surveyapp:all_token_survey', survey_token=survey.survey_token)

        
    # print()
    # Render the form with context data for GET requests
    context = {
        'survey': survey,
        'questions': survey.questions.all(),  # Questions for display
        'contacts': contacts,  # All contacts related to the survey
        'contact_details': contact_details,  # Detailed contact info if needed
        'assigned_contact': assigned_contact,  # Contact to show in the form
    }
    return render(request, 'poltaker/take_survey.html', context)

# surveyapp/views.py
from django.shortcuts import render
from .models import Survey

# Survey list view
def survey_list(request):
    surveys = Survey.objects.all()  # Retrieve all surveys from the database
    return render(request, 'poltaker/survey_list.html', {'surveys': surveys})

 

from .models import Survey, SurveyResponse

# def poltaker_dashboard(request):
#     if 'poltaker_id' not in request.session:
#         return redirect('surveyapp:poltaker_login')
    
   

#     poltaker = Poltaker.objects.get(id=request.session['poltaker_id'])
#     assigned_surveys = Survey.objects.filter(polltaker=poltaker)
#     context = {'poltaker': poltaker, 'surveys': assigned_surveys}
    
#     return render(request, 'poltaker/dashboard.html', context)

def poltaker_account(request):
    if 'poltaker_id' not in request.session:
        return redirect('surveyapp:poltaker_login')
    
    # Get the Poltaker using the ID stored in session
    poltaker = Poltaker.objects.get(id=request.session['poltaker_id'])
    
    # Add any other Poltaker details you want to display
    context = {
        'poltaker': poltaker,
    }
    
    return render(request, 'poltaker/account.html', context)



def all_the_survey(request):
    if 'poltaker_id' not in request.session:
        return redirect('surveyapp:poltaker_login')
    
   

    poltaker = Poltaker.objects.get(id=request.session['poltaker_id'])
    assigned_surveys = Survey.objects.filter(polltaker=poltaker)
    context = {'poltaker': poltaker, 'surveys': assigned_surveys}
    
    return render(request, 'poltaker/all_the_survey.html', context)
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# Survey list view

# from walkapp.models import UserSubscription
# @login_required 
# def trial_user(request):
#     user_subscription = UserSubscription.objects.filter(user=request.user).first()

#     context = {'subscription': user_subscription}

#     contacts_limit = user_subscription.plan.contacts  # Ensure this attribute exists
#     print(f"{contacts_limit}")
#     return render(request, 'test/test.html', context)

from .models import Survey, SurveyResponse



def test_survay(request):
    return render(request,'poltaker/ztest_survey.html')

# Poltaker survay details showing - complete , inprogress , pending view down here 
from django.shortcuts import get_object_or_404
from .models import Survey, Poltaker
from django.contrib import messages
from django.shortcuts import redirect

def update_survey_status(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id)

    if request.method == 'POST':
        status = request.POST.get('status')  # Assuming status is sent from a form or API

        if status not in ['pending', 'in_progress', 'completed']:
            messages.error(request, "Invalid status.")
            return redirect('surveyapp:survey_list')

        # Update the survey's status
        survey.status = status
        survey.save()

        # Update Poltaker counts based on survey status
        poltaker = survey.polltaker

        if status == 'completed':
            poltaker.completed_surveys += 1
            poltaker.inprogress_surveys -= 1
        elif status == 'in_progress':
            poltaker.inprogress_surveys += 1
            poltaker.pending_surveys -= 1
        elif status == 'pending':
            poltaker.pending_surveys += 1

        # Save the updated Poltaker object
        poltaker.save()

        # Update total surveys
        poltaker.total_survey = poltaker.completed_surveys + poltaker.inprogress_surveys + poltaker.pending_surveys
        poltaker.save()

        messages.success(request, f"Survey status updated to {status}.")
        return redirect('surveyapp:survey_list')

    return redirect('surveyapp:survey_list')



# complete survey --------------------------------------------------------------------------------------------
from django.shortcuts import get_object_or_404, redirect
from .models import Survey, Poltaker
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib import messages

from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from .models import Survey, Poltaker, UserContactList
def complete_survey(request, survey_id):
    # Get the survey or return a 404 if it doesn't exist
    survey = get_object_or_404(Survey, id=survey_id)

    # Fetch the Poltaker from the session to ensure they are logged in
    poltaker_id = request.session.get('poltaker_id')
    if not poltaker_id:
        return JsonResponse({'status': 'error', 'message': 'Poltaker not logged in!'})  # Return an error if Poltaker isn't logged in

    try:
        poltaker = Poltaker.objects.get(id=poltaker_id)
    except Poltaker.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Poltaker not found!'})  # Return an error if Poltaker isn't found

    # Check if the poltaker is authorized to take this survey
    if survey.polltaker and poltaker != survey.polltaker:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized access to survey!'})  # Unauthorized access

    # Mark the survey as completed and update the status
    if survey.status != 'completed':  # Only update if not already completed
        survey.status = 'completed'
        survey.save()

        # Get the contacts related to this specific survey
        contacts_related_to_survey = survey.contacts.all()

        # Find all surveys that are assigned to the same contacts
        related_surveys = Survey.objects.filter(contacts__in=contacts_related_to_survey).distinct()

        # Update the status of these related surveys
        for related_survey in related_surveys:
            # Check if the contact is related to this specific survey and mark it as completed
            if any(contact in contacts_related_to_survey for contact in related_survey.contacts.all()):
                related_survey.status = 'completed'
                related_survey.save()

        # Now, update the status of all the related contacts as well
        for contact in contacts_related_to_survey:
            contact.status = 'completed'  # Assuming you have a `status` field on the Contact model
            contact.save()

    # Return a JsonResponse to confirm that the survey is completed and stay on the same page
    return JsonResponse({'status': 'success', 'message': 'Survey completed successfully!'})

def deny_survey(request, survey_id):
    # Get the survey or return a 404 if it doesn't exist
    survey = get_object_or_404(Survey, id=survey_id)

    # Fetch the Poltaker from the session to ensure they are logged in
    poltaker_id = request.session.get('poltaker_id')
    if not poltaker_id:
        return redirect('surveyapp:poltaker_login')  # Redirect to login if Poltaker isn't logged in

    try:
        poltaker = Poltaker.objects.get(id=poltaker_id)
    except Poltaker.DoesNotExist:
        return redirect('surveyapp:poltaker_login')  # Redirect if the Poltaker isn't found

    # Check if the poltaker is authorized to take this survey
    if survey.polltaker and poltaker != survey.polltaker:
        return redirect('surveyapp:poltaker_dashboard')  # Redirect if the Poltaker is unauthorized

    # Mark the survey as denied and update the status
    if survey.status != 'denied':  # Only update if not already denied
        survey.status = 'denied'
        survey.save()

        # Update the UserContactList status to 'denied'
        for contact in survey.contacts.all():
            contact.status = 'denied'
            contact.save()

        messages.success(request, 'Survey marked as denied successfully!')

    # Redirect to the dashboard after denying the survey
    return redirect('surveyapp:poltaker_dashboard')














# new dashbaord  -----------------------------------------------------------------------------------------

def poltaker_dashboard(request):
    # Check if the polltaker is logged in
    if 'poltaker_id' not in request.session:
        return redirect('surveyapp:poltaker_login')

    # Get the current logged-in polltaker
    poltaker = Poltaker.objects.get(id=request.session['poltaker_id'])

    # Get all surveys assigned to the polltaker
    assigned_surveys = Survey.objects.filter(polltaker=poltaker)

    # Exclude surveys that are marked as 'completed'
    incomplete_surveys = assigned_surveys.exclude(status='completed')

    # Group surveys by their token (only show unique tokens)
    surveys_by_token = {}
    for survey in incomplete_surveys:
        if survey.survey_token not in surveys_by_token:
            surveys_by_token[survey.survey_token] = survey

    if 'poltaker_id' not in request.session:
        return redirect('surveyapp:poltaker_login')
    
    # Get the Poltaker using the ID stored in session
    poltaker = Poltaker.objects.get(id=request.session['poltaker_id'])
    
    # Pass the context for rendering the dashboard
    context = {'poltaker': poltaker,'poltaker': poltaker, 'surveys': surveys_by_token.values()}
    return render(request, 'poltaker/dashboard.html', context)

def assigned_surveys_poltaker(request):
    # Check if the polltaker is logged in
    if 'poltaker_id' not in request.session:
        return redirect('surveyapp:poltaker_login')

    # Get the current logged-in polltaker
    poltaker = Poltaker.objects.get(id=request.session['poltaker_id'])

    # Get all surveys assigned to the polltaker
    assigned_surveys = Survey.objects.filter(polltaker=poltaker)

    # Exclude surveys that are marked as 'completed'
    incomplete_surveys = assigned_surveys.exclude(status='completed')

    # Group surveys by their token (only show unique tokens)
    surveys_by_token = {}
    for survey in incomplete_surveys:
        if survey.survey_token not in surveys_by_token:
            surveys_by_token[survey.survey_token] = survey

    if 'poltaker_id' not in request.session:
        return redirect('surveyapp:poltaker_login')
    
    # Get the Poltaker using the ID stored in session
    poltaker = Poltaker.objects.get(id=request.session['poltaker_id'])
    
    # Pass the context for rendering the dashboard
    context = {'poltaker': poltaker,'poltaker': poltaker, 'surveys': surveys_by_token.values()}
    return render(request, 'poltaker/assigned_surveys.html', context)



from django.db.models import Count, Q
def all_token_survey(request, survey_token):
    if 'poltaker_id' not in request.session:
        return redirect('surveyapp:poltaker_login')

    poltaker = Poltaker.objects.get(id=request.session['poltaker_id'])

    # Fetch surveys with at least one contact not marked as 'completed' or 'denied' and exclude surveys that are already 'completed'
    surveys = Survey.objects.filter(
        survey_token=survey_token,
        polltaker=poltaker
    ).exclude(status='completed').annotate(
        valid_contacts=Count('contacts', filter=~Q(contacts__status__in=['completed', 'denied']))
    ).filter(valid_contacts__gt=0)

    context = {'poltaker': poltaker, 'surveys': surveys}
    return render(request, 'poltaker/all_token_survey.html', context)

# Poltaker information edit start -----------------------------------------
# views.py
from django.shortcuts import render, redirect
from walkapp.models import Poltaker
from django.contrib.auth.models import User
from django.db import IntegrityError

def edit_poltaker_profile(request):
    try:
        # Retrieve the Poltaker ID from the session
        poltaker_id = request.session.get('poltaker_id')
        if not poltaker_id:
            return redirect('surveyapp:poltaker_login')  # Redirect to login if no Poltaker is logged in

        # Fetch the Poltaker instance by ID
        poltaker = Poltaker.objects.get(id=poltaker_id)

        # Check if it's a POST request (form submission)
        if request.method == 'POST':
            # Get form data
            name = request.POST.get('name')
            mobile = request.POST.get('mobile')
            email = request.POST.get('email')
            zip_code = request.POST.get('zip_code')
            street = request.POST.get('Street')
            city = request.POST.get('city')
            state = request.POST.get('state')

            # Check for duplicate email
            if Poltaker.objects.filter(email=email).exclude(id=poltaker.id).exists():
                messages.error(request, "The email is already in use. Please choose a different email.")
                return render(request, 'poltaker/edit_poltaker_profile.html', {'poltaker': poltaker})

            # Update the Poltaker details
            poltaker.name = name
            poltaker.mobile = mobile
            poltaker.email = email
            poltaker.zip_code = zip_code
            poltaker.Street = street
            poltaker.city = city
            poltaker.state = state

            poltaker.save()  # Save the updated Poltaker object to the database

            messages.success(request, "Your profile has been updated successfully!")
            return redirect('surveyapp:edit_poltaker_profile')  # Reload the page to show success message

        return render(request, 'poltaker/edit_poltaker_profile.html', {'poltaker': poltaker})

    except Poltaker.DoesNotExist:
        messages.error(request, "Poltaker not found.")
        return redirect('surveyapp:poltaker_login')  # Redirect to login page if Poltaker doesn't exist

# Poltaker information edit start -----------------------------------------


