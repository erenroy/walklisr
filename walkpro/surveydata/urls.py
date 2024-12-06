# surveydata/urls.py
from django.urls import path
from . import views

app_name = 'surveydata'  # Using this namespace for this app

urlpatterns = [
    path('my-surveys/', views.my_surveys, name='my_surveys'),  # List surveys created by the logged-in user
    path('export-responses/<int:survey_id>/', views.export_responses_as_csv, name='export_responses'),  # Export CSV

    path('delete_survey/<int:survey_id>/', views.delete_survey, name='delete_survey'),
    path('edit_survey/<int:survey_id>/', views.edit_survey, name='edit_survey'),
    path('view/<int:survey_id>/', views.view_responses, name='view_responses'),
    
]
