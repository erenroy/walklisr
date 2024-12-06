
# ADding survey data for user 
# views.py of walkapp
import csv
from django.http import HttpResponse
from django.shortcuts import render
from surveyapp.models import Survey, SurveyResponse  # Import the models from surveyapp

# View 
import csv
from django.http import HttpResponse
from surveyapp.models import SurveyResponse, Survey  # Import from surveyapp
from walkapp.models import Question, Option  # Import from walkapp
from walkapp.models import Poltaker  # Import Poltaker model



from collections import defaultdict

def my_surveys(request):
    # Ensure the user is logged in and filter surveys based on user (created_by)
    surveys = Survey.objects.filter(created_by=request.user)
    
    # Group surveys by survey_token
    survey_groups = defaultdict(list)
    for survey in surveys:
        survey_groups[survey.survey_token].append(survey)

    unique_surveys = []
    for survey_token, group in survey_groups.items():
        # Check how many surveys in the group are completed
        completed_count = sum(survey.status == 'completed' for survey in group)
        
        # Determine if at least half of the surveys are completed
        total_surveys = len(group)
        polltaker_count = len(set(survey.polltaker for survey in group))
        required_completed = total_surveys / polltaker_count

        # Get a representative survey (e.g., the first one) and update its status
        representative_survey = group[0]
        representative_survey.status = 'completed' if completed_count >= required_completed else 'pending'
        unique_surveys.append(representative_survey)

    username = request.user.username if request.user.is_authenticated else None
    
    context = {
        'surveys': unique_surveys,
        'username': username
    }
    return render(request, 'surveydata/my_surveys.html', context)
import csv
from django.http import HttpResponse
from surveyapp.models import SurveyResponse, Survey  # Import from surveyapp
from walkapp.models import Question, Option  # Import from walkapp
from walkapp.models import Poltaker  # Import Poltaker model
import csv
from django.http import HttpResponse
from surveyapp.models import Survey, SurveyResponse


def export_responses_as_csv(request, survey_id):
    # Get the selected survey object
    survey = Survey.objects.get(id=survey_id)

    # Fetch all surveys with the same token
    surveys_with_same_token = Survey.objects.filter(survey_token=survey.survey_token)

    # Create the HttpResponse with CSV content type
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{survey.title}_responses.csv"'

    # Create a CSV writer
    writer = csv.writer(response)

    # Prepare header row
    header = ['Survey Name', 'Survey Date', 'Polltaker Name', 'Polltaker Mobile', 'Polltaker Email',
              'Contact Name', 'Contact Email']

    # Add question text to the header
    questions = list(survey.questions.all())  # List of questions for this survey

    # Add question text to the header
    for question in questions:
        header.append(question.question_text)

    # Add Denial Reason to the header
    header.append('Denial Reason')  # Add a column for the denial reason

    writer.writerow(header)  # Write the header row to the CSV

    # Loop through each survey with the same token and export responses
    for survey in surveys_with_same_token:
        # Fetch all responses for this survey
        responses = SurveyResponse.objects.filter(survey=survey)

        # Loop through each survey response and write data to the CSV
        for response_data in responses:
            row = [survey.title, survey.survey_date]  # Survey name and date

            # Polltaker Data
            polltaker = response_data.polltaker
            row.append(f'{polltaker.name}')  # Polltaker's name
            row.append(polltaker.mobile)  # Polltaker's mobile
            row.append(polltaker.email)  # Polltaker's email

            # Contact Name and Email (Ensure the contact is assigned to the survey)
            contact = response_data.contact  # ForeignKey reference
            row.append(f'{contact.first_name} {contact.last_name}' if contact else '')  # Full name of the contact
            row.append(contact.email if contact else '')  # Contact's email

            # Loop through each question and its corresponding answer
            for question in questions:
                answer = ''
                # If the question is of type 'mcq' (Multiple Choice)
                if question.question_type == 'mcq':
                    selected_option = response_data.responses.get(question.question_text, {}).get('selected_option', '')
                    answer = selected_option  # Get the selected option

                # If the question is of type 'text' (Open Text)
                elif question.question_type == 'text':
                    answer = response_data.responses.get(question.question_text, {}).get('answer_text', '')

                # If the question is of type 'yesno' (Yes/No)
                elif question.question_type == 'yesno':
                    answer = response_data.responses.get(question.question_text, {}).get('answer_text', '')

                row.append(answer)  # Append the answer to the row

            # Add Denial Reason if available
            denial_reason = response_data.denial_reason if hasattr(response_data, 'denial_reason') else ''
            row.append(denial_reason)  # Append the denial reason to the row

            writer.writerow(row)  # Write the row to the CSV

    return response


# views.py
from django.shortcuts import render, redirect, get_object_or_404
from surveyapp.models import Survey  # Assuming your model is named 'Survey'
# views.py
from django.shortcuts import render, redirect, get_object_or_404
from surveyapp.models import Survey



def delete_survey(request, survey_id):
    print(f"Received request to delete survey with ID: {survey_id}")  # Debug: Check if function is called

    if request.method == 'POST':
        print("Request method is POST")  # Debug: Confirm request method
        # Get the survey object by its ID or return a 404 if not found
        survey = get_object_or_404(Survey, id=survey_id)
        survey_token = survey.survey_token
        
        # Fetch all surveys with the same survey_token
        surveys_to_delete = Survey.objects.filter(survey_token=survey_token)
        print(f"Surveys to delete: {surveys_to_delete}")  # Debug: List surveys to delete

        # Delete all surveys with the same survey_token
        surveys_to_delete.delete()
        print("Surveys deleted successfully")  # Debug: Confirm deletion

        # Redirect to the list of surveys after deletion
        return redirect('surveydata:my_surveys')
    else:
        print("Request method is not POST, redirecting to survey list")  # Debug: Handle non-POST request
        return HttpResponseNotAllowed(['POST'])



# # View to export responses for a survey as CSV
# def export_responses_as_csv(request, survey_id):                            this view does not work 
#     # Get the survey object
#     survey = Survey.objects.get(id=survey_id)

#     # Fetch all responses for this survey
#     responses = SurveyResponse.objects.filter(survey=survey)

#     # Create the HttpResponse with CSV content type
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = f'attachment; filename="{survey.title}_responses.csv"'

#     # Create a CSV writer
#     writer = csv.writer(response)

#     # Prepare header row
#     header = ['Survey Name', 'Polltaker Name', 'Polltaker Mobile', 'Polltaker Email', 'Polltaker Zip Code', 
#               'Polltaker Street', 'Polltaker City', 'Polltaker State', 'Contact Name', 'Contact Email']  # Adjusted header

#     # Add question text to the header
#     questions = list(survey.questions.all())  # List of questions for this survey

#     # Add question text to the header
#     for question in questions:
#         header.append(question.question_text)

#     writer.writerow(header)  # Write the header row to the CSV

#     # Loop through each survey response and write data to the CSV
#     for response_data in responses:
#         row = [survey.title]  # Survey name
        
#         # Polltaker Data
#         polltaker = response_data.polltaker
#         row.append(f'{polltaker.name}')  # Polltaker's name
#         row.append(polltaker.mobile)  # Polltaker's mobile
#         row.append(polltaker.email)  # Polltaker's email
#         row.append(polltaker.zip_code)  # Polltaker's zip code
#         row.append(polltaker.Street)  # Polltaker's street
#         row.append(polltaker.city)  # Polltaker's city
#         row.append(polltaker.state)  # Polltaker's state

#         # Contact Name and Email (Ensure the contact is assigned to the survey)
#         contact = response_data.contact  # ForeignKey reference
#         row.append(f'{contact.first_name} {contact.last_name}' if contact else '')  # Full name of the contact
#         row.append(contact.email if contact else '')  # Contact's email
        
#         # Loop through each question and its corresponding answer
#         for question in questions:
#             answer = ''
#             # If the question is of type 'mcq' (Multiple Choice)
#             if question.question_type == 'mcq':
#                 selected_option = response_data.responses.get(question.question_text, {}).get('selected_option', '')
#                 answer = selected_option  # Get the selected option

#             # If the question is of type 'text' (Open Text)
#             elif question.question_type == 'text':
#                 answer = response_data.responses.get(question.question_text, {}).get('answer_text', '')

#             # If the question is of type 'yesno' (Yes/No)
#             elif question.question_type == 'yesno':
#                 answer = response_data.responses.get(question.question_text, {}).get('answer_text', '')

#             row.append(answer)  # Append the answer to the row
        
#         writer.writerow(row)  # Write the row to the CSV

#     return response










# -------------------------------------------------------------------------------------
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required  # Import the login_required decorator
from walkapp.models import Question, Poltaker, UserContactList
from surveyapp.models import Survey
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone


@login_required
def edit_survey(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id)
    
    # Check if any survey with the same survey_token has a status other than 'pending'
    surveys_with_same_token = Survey.objects.filter(survey_token=survey.survey_token)
    
    if surveys_with_same_token.exclude(status='pending').exists():
        # If any survey has a status other than 'pending', deny access to edit
        messages.error(request, 'You cannot edit the survey because it has already started or Completed')
        return redirect('surveydata:my_surveys')
    
    # print(survey.status)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        survey_date = request.POST.get('survey_date')
        
        # Get the selected questions from the form
        question_ids = request.POST.getlist('questions')  # Get selected question IDs

        if not survey_date:
            survey_date = timezone.now().date()  # Default to today's date
        else:
            survey_date = timezone.datetime.strptime(survey_date, '%Y-%m-%d').date()  # Parse input date
        
        # Update the current survey with the new title, description, and survey_date
        survey.title = title
        survey.description = description
        survey.survey_date = survey_date
        
        # Set the selected questions for the current survey
        selected_questions = Question.objects.filter(id__in=question_ids, user=request.user)
        survey.questions.set(selected_questions)
        
        survey.save()
        
        # Update all surveys with the same survey_token
        for s in surveys_with_same_token:
            if s != survey:  # Don't update the current survey again
                s.title = title
                s.description = description
                s.survey_date = survey_date
                s.questions.set(selected_questions)  # Update questions for this survey
                s.save()
        
        messages.success(request, 'Survey updated successfully for all associated surveys.')
        return redirect('surveydata:my_surveys')
    
    # Pass the survey and all available questions to the template for rendering
    questions = Question.objects.filter(user=request.user)
    context = {
        'survey': survey,
        'questions': questions,
    }
    return render(request, 'surveyapp/edit_survey.html', context)

# Edit survey ends here 







# new cieww -----------------------------------------------------


def view_responses(request, survey_id):
    # Get the selected survey object
    survey = Survey.objects.get(id=survey_id)

    # Fetch all surveys with the same token
    surveys_with_same_token = Survey.objects.filter(survey_token=survey.survey_token)

    # Prepare data to be displayed in the browser
    data = []

    # Prepare header row
    header = ['Survey Name', 'Survey Date', 'Polltaker Name', 'Polltaker Mobile', 'Polltaker Email',
              'Contact Name', 'Contact Email']

    # Add question text to the header
    questions = list(survey.questions.all())  # List of questions for this survey
    for question in questions:
        header.append(question.question_text)
    header.append('Denial Reason')  # Add a column for the denial reason
    data.append(header)

    # Loop through each survey with the same token and export responses
    for survey in surveys_with_same_token:
        # Fetch all responses for this survey
        responses = SurveyResponse.objects.filter(survey=survey)

        # Loop through each survey response and prepare data for the browser
        for response_data in responses:
            row = [survey.title, survey.survey_date.strftime('%Y-%m-%d')]  # Survey name and formatted date

            # Polltaker Data
            polltaker = response_data.polltaker
            row.append(polltaker.name)  # Polltaker's name
            row.append(polltaker.mobile)  # Polltaker's mobile
            row.append(polltaker.email)  # Polltaker's email

            # Contact Name and Email (Ensure the contact is assigned to the survey)
            contact = response_data.contact  # ForeignKey reference
            row.append(f'{contact.first_name} {contact.last_name}' if contact else '')  # Full name of the contact
            row.append(contact.email if contact else '')  # Contact's email

            # Loop through each question and its corresponding answer
            for question in questions:
                answer = ''
                # If the question is of type 'mcq' (Multiple Choice)
                if question.question_type == 'mcq':
                    selected_option = response_data.responses.get(question.question_text, {}).get('selected_option', '')
                    answer = selected_option  # Get the selected option

                # If the question is of type 'text' (Open Text)
                elif question.question_type == 'text':
                    answer = response_data.responses.get(question.question_text, {}).get('answer_text', '')

                # If the question is of type 'yesno' (Yes/No)
                elif question.question_type == 'yesno':
                    answer = response_data.responses.get(question.question_text, {}).get('answer_text', '')

                row.append(answer)  # Append the answer to the row

            # Add Denial Reason if available
            denial_reason = response_data.denial_reason if hasattr(response_data, 'denial_reason') else ''
            row.append(denial_reason)  # Append the denial reason to the row

            data.append(row)  # Append the row to the data list

    context = {
        'survey': survey,
        'data': data,
    }

    return render(request, 'surveydata/view_responses.html', context)