from django.contrib import admin
from .models import PersonData , UserProfile , UserSubscriptionDetails , Question , Option , PasswordReset

class PersonDataAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'city', 'state', 'country', 'party_preference')
    search_fields = ('first_name', 'last_name', 'email', 'city')

admin.site.register(PersonData, PersonDataAdmin)

# admin.py
from django.contrib import admin
from .models import SubscriptionPlan, UserSubscription

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'managers', 'poltakers', 'surveys', 'contacts')


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'start_date')

admin.site.register(UserProfile)


from .models import UserSearch

admin.site.register(UserSearch)


# admin.py
from django.contrib import admin
from .models import UserContactAccess

@admin.register(UserContactAccess)
class UserContactAccessAdmin(admin.ModelAdmin):
    list_display = ('user', 'person', 'accessed_at')
    search_fields = ('user__username', 'person__first_name', 'person__last_name')
    list_filter = ('accessed_at',)


# admin.site.register(UserSubscriptionDetails)


# admin.py
from django.contrib import admin
from .models import Poltaker

@admin.register(Poltaker)
class PoltakerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'zip_code', 'user')
    search_fields = ('name', 'email', 'user__username')
    list_filter = ('user',)



from django.contrib import admin
from .models import Question, Option

# class OptionInline(admin.TabularInline):
#     model = Option
#     extra = 1  # Allows adding one extra empty option by default

# class QuestionAdmin(admin.ModelAdmin):
#     list_display = ('question_text', 'question_type', 'user')
#     search_fields = ('question_text',)
#     list_filter = ('question_type', 'user')
#     inlines = [OptionInline]  # Show options inline within the question admin page

# admin.site.register(Question, QuestionAdmin)
# admin.site.register(Option)  # Option can be managed separately if needed

from django.contrib import admin
from .models import GeneralQuestion
from django import forms
from django.contrib import admin
from .models import GeneralQuestion

class GeneralQuestionForm(forms.ModelForm):
    class Meta:
        model = GeneralQuestion
        fields = '__all__'
        widgets = {
            'options': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter options, one per line'}),
        }

class GeneralQuestionAdmin(admin.ModelAdmin):
    form = GeneralQuestionForm
    list_display = ('question_text', 'question_type')
    search_fields = ('question_text',)

admin.site.register(GeneralQuestion, GeneralQuestionAdmin)


admin.site.register(PasswordReset)




# admin.py
from django.contrib import admin
from .models import UserContactList

@admin.register(UserContactList)
class UserContactListAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'city', 'state', 'country', 'party_preference')
    list_filter = ('party_preference', 'country')
    search_fields = ('first_name', 'last_name', 'email', 'city', 'state', 'country', 'zip_code')

# Optionally, you can register without using the decorator:
# admin.site.register(UserContactList, UserContactListAdmin)
from django.contrib import admin
from .models import UserContactSearch

admin.site.register(UserContactSearch)



# admin.py
from django.contrib import admin





# questions/admin.py

from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from .models import Question
class QuestionAdmin(admin.ModelAdmin):
    change_list_template = "admin/questions_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-csv/', self.admin_site.admin_view(self.upload_csv))
        ]
        return custom_urls + urls

    def upload_csv(self, request):
        return redirect("upload_csv")

admin.site.register(Question, QuestionAdmin)