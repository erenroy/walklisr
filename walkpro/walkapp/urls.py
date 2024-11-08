# walkapp/urls.py

from django.urls import path
from .views import register, login_view, logout_view, home_view , cdata_view
from .views import subscription_plans, choose_plan, process_payment, subscription_success , personal_details_plan , user_details , accessed_contacts
from . import views
from .views import search_person_data , add_poltaker , add_questions , view_questions , first_look , verify_otp
from django.conf import settings
from django.conf.urls.static import static

from .views import ForgotPassword, PasswordResetSent, ResetPassword , question_search ,   poltaker_change_password , upload_contacts
from .views import contact_list ,contact_search ,contact_search_results
from .views import download_poltakers_csv


# app_name = 'walkapp'  # This is the namespace for this app

urlpatterns = [
    path('',first_look, name='first_look'),
    path('login/', login_view, name='login_view'),
    path('register/', register, name='register'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('home/', home_view, name='home'),
    path('cdata/', cdata_view, name='cdata'),
    path('subscriptions/', subscription_plans, name='subscription_plans'),
    path('subscriptions/choose/<int:plan_id>/', choose_plan, name='choose_plan'),
    path('subscriptions/process_payment/', process_payment, name='process_payment'),
    path('subscriptions/success/', subscription_success, name='subscription_success'),
    path('subscriptions/execute/', views.execute_payment, name='execute_payment'),
    path('plannotice/', views.plannotice, name='plannotice'),  # Add this line
    path('homes/', views.homes, name='homes'),  # Add this line
    path('testcase', views.testcase, name='testcase'),
    path('personal-details/', personal_details_plan, name='personal_details_plan'),
    path('user-details/', user_details, name='user_details'), # For my account 
    # payment done next urls -------------------------------------------------------------------------
    # path('state-query/', state_query, name='state_query'),
    # path('state-data/<str:state>/', state_data_detail, name='data_detail'),  # New URL pattern
    # path('results/', views.show_results, name='show_results'),
    path('search/', search_person_data, name='search_person_data'),
    path('accessed-contacts/', accessed_contacts, name='accessed_contacts'),
    # path('poltaker_page/',  poltaker_page, name=' poltaker_page'),

    # poltaker urls 
    path('add-poltaker/', views.add_poltaker, name='add_poltaker'),
    # path('poltaker/login/', views.poltaker_login, name='poltaker_login'),                                    0000000000
    # path('poltaker/dashboard/', views.poltaker_dashboard, name='poltaker_dashboard'),                        0000000000
    # path('poltaker/logout/', views.poltaker_logout, name='poltaker_logout'),                                 0000000000
    path('add-questions/', views.add_questions, name='add_questions'),
    path('view/', views.view_questions, name='view_questions'),  # New URL for viewing questions
    path('survey_work/', views.survey_work, name='survey_work'),  # New URL for viewing questions

    path('forgot-password/', ForgotPassword, name='forgot-password'),
    path('password-reset-sent/<uuid:reset_id>/', PasswordResetSent, name='password-reset-sent'),
    path('reset-password/<uuid:reset_id>/', ResetPassword, name='reset-password'),
    path('question-search/', question_search, name='question_search'),
    
    # path('test-questions/', test_model_questions, name='test_questions'),  # Add this line    0---------- No use now 
    # path('poltaker/change-password/', poltaker_change_password, name='poltaker_change_password'),  # Add this line           00000000000

    # adding contact 
    path('upload-contacts/', upload_contacts, name='upload_contacts'),
    path('contacts/', contact_list, name='contacts_list'),  # This should match the view name
    # path('test/',test_details, name='test_details')
    path('contact_search/', contact_search, name='contact_search'),
    path('contact_search/results/', contact_search_results, name='contact_search_results'),


    # next working download 
    path('download-contacts/', views.download_contacts_csv, name='download_contacts_csv'),
    path('download-poltakers/', download_poltakers_csv, name='download_poltakers_csv'),
    

    # survey data 
    # path('my-surveys/', views.my_surveys, name='my_surveys'), 
    # path('export-responses/<int:survey_id>/', views.export_responses_as_csv, name='export_responses'),  # Export responses
]
# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

