# surveyapp/admin.py
from django.contrib import admin
from .models import Survey, SurveyResponse
from walkapp.models import Poltaker, Question  # Assuming Poltaker and Question are in walkapp

class SurveyAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'polltaker', 'created_at')
    search_fields = ('title', 'description', 'created_by__username', 'polltaker__user__username')

class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ('survey', 'polltaker', 'submitted_at')
    search_fields = ('survey__title', 'polltaker__user__username')
    readonly_fields = ('submitted_at',)
    
    def responses_display(self, obj):
        return obj.responses
    responses_display.short_description = 'Responses'

admin.site.register(Survey, SurveyAdmin)
admin.site.register(SurveyResponse, SurveyResponseAdmin)
