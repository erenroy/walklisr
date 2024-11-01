from django.contrib import admin
from .models import PersonData , UserProfile , UserSubscriptionDetails , Question , Option

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

class OptionInline(admin.TabularInline):
    model = Option
    extra = 6  # Allow adding up to 6 options

class QuestionAdmin(admin.ModelAdmin):
    inlines = [OptionInline]

admin.site.register(Question, QuestionAdmin)
