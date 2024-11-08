# # surveyapp/urls.py
# from django.urls import path
# from . import views

# app_name = 'surveyapp'

# urlpatterns = [
#     path('create-survey/', views.create_survey, name='create_survey'),
#     path('polltaker-surveys/', views.polltaker_surveys, name='polltaker_surveys'),
#     path('dashboard/', views.poltaker_dashboard, name='poltaker_dashboard'),
#     path('login/', views.poltaker_login, name='poltaker_login'),
#     path('logout/', views.poltaker_logout, name='poltaker_logout'),  # Logout URL
# ]
from django.urls import path
from . import views

app_name = 'surveyapp'  # Set the app name to 'surveyapp' for namespace

urlpatterns = [
    path('login/', views.poltaker_login, name='poltaker_login'),
    # path('change-password/', views.change_password, name='change_password'),
    path('password-change/', views.password_change, name='password_change'),
    path('dashboard/', views.poltaker_dashboard, name='poltaker_dashboard'),
    path('logout/', views.poltaker_logout, name='poltaker_logout'),
    path('create/', views.create_survey, name='create_survey'),  # URL for creating a new survey
    path('take-survey/<int:survey_id>/', views.take_survey, name='take_survey'),  # URL for poltaker to answer a specific survey
    path('list/', views.survey_list, name='survey_list'),        # Survey list view
    # path('trial_user/',views.trial_user, name='trial_user')
    path('test_survay/',views.test_survay,name="test_survay"),

    path('forgot-password/', views.forgot_password, name='forgot_password'),  # Forgot Password URL
    path('reset-password/', views.reset_password, name='reset_password'),  # Reset Password URL
    path('survey/update_status/<int:survey_id>/', views.update_survey_status, name='update_survey_status'),
    path('complete-survey/<int:survey_id>/', views.complete_survey, name='complete_survey'),

    path('poltaker_account/', views.poltaker_account, name='poltaker_account' ),
    path('all_the_survey',views.all_the_survey, name='all_the_survey')
    # survay data 
    

]
