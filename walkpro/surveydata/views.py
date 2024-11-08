
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




# View to display surveys created by the logged-in user
def my_surveys(request):
    # Ensure the user is logged in and filter surveys based on user (created_by)
    surveys = Survey.objects.filter(created_by=request.user)
    username = request.user.username if request.user.is_authenticated else None
    
    context = {
        'surveys': surveys,
        'username':username
    }
    return render(request, 'surveydata/my_surveys.html', context)

import csv
from django.http import HttpResponse
from surveyapp.models import SurveyResponse, Survey  # Import from surveyapp
from walkapp.models import Question, Option  # Import from walkapp
from walkapp.models import Poltaker  # Import Poltaker model

def export_responses_as_csv(request, survey_id):
    # Get the survey object
    survey = Survey.objects.get(id=survey_id)

    # Fetch all responses for this survey
    responses = SurveyResponse.objects.filter(survey=survey)

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

    writer.writerow(header)  # Write the header row to the CSV

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
        
        writer.writerow(row)  # Write the row to the CSV

    return response


# views.py
from django.shortcuts import render, redirect, get_object_or_404
from surveyapp.models import Survey  # Assuming your model is named 'Survey'
# views.py
from django.shortcuts import render, redirect, get_object_or_404
from surveyapp.models import Survey

def delete_survey(request, survey_id):
    # Get the survey object by its ID or return a 404 if not found
    survey = get_object_or_404(Survey, id=survey_id)
    
    # Delete the survey (no check for the 'creator')
    survey.delete()

    # Redirect to the list of surveys after deletion
    return redirect('surveydata:my_surveys')

# # View to export responses for a survey as CSV
# def export_responses_as_csv(request, survey_id):
    # Get the survey object
    survey = Survey.objects.get(id=survey_id)

    # Fetch all responses for this survey
    responses = SurveyResponse.objects.filter(survey=survey)

    # Create the HttpResponse with CSV content type
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{survey.title}_responses.csv"'

    # Create a CSV writer
    writer = csv.writer(response)

    # Prepare header row
    header = ['Survey Name', 'Polltaker Name', 'Polltaker Mobile', 'Polltaker Email', 'Polltaker Zip Code', 
              'Polltaker Street', 'Polltaker City', 'Polltaker State', 'Contact Name', 'Contact Email']  # Adjusted header

    # Add question text to the header
    questions = list(survey.questions.all())  # List of questions for this survey

    # Add question text to the header
    for question in questions:
        header.append(question.question_text)

    writer.writerow(header)  # Write the header row to the CSV

    # Loop through each survey response and write data to the CSV
    for response_data in responses:
        row = [survey.title]  # Survey name
        
        # Polltaker Data
        polltaker = response_data.polltaker
        row.append(f'{polltaker.name}')  # Polltaker's name
        row.append(polltaker.mobile)  # Polltaker's mobile
        row.append(polltaker.email)  # Polltaker's email
        row.append(polltaker.zip_code)  # Polltaker's zip code
        row.append(polltaker.Street)  # Polltaker's street
        row.append(polltaker.city)  # Polltaker's city
        row.append(polltaker.state)  # Polltaker's state

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
        
        writer.writerow(row)  # Write the row to the CSV

    return response