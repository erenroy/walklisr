# walkapp/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import PersonData
from django.contrib.auth.decorators import login_required
# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import SubscriptionPlan, UserSubscription , UserSubscriptionDetails
from django.conf import settings
import paypalrestsdk

def first_look(request):
    return render(request, 'look/index.html')
    
def register(request):
    if request.method == 'POST':
        username = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if username and email and password:
            try:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                messages.success(request, 'Registration successful! You can now log in.')
                return redirect('login')
            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')
        else:
            messages.error(request, 'Please fill in all fields.')
    return render(request, 'register.html')

# walkapp/views.py
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Attempt to authenticate the user using the email as username
        try:
            user = User.objects.get(email=email)  # Get user by email
            user = authenticate(request, username=user.username, password=password)  # Authenticate
            
            if user is not None:
                login(request, user)  # Log in the user
                return redirect('subscription_plans')  # Redirect to home page
            else:
                messages.error(request, 'Invalid email or password.')
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password.')  # Handle case where user doesn't exist

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def home_view(request):
    user_subscription = UserSubscription.objects.filter(user=request.user).first()

    username = request.user.username if request.user.is_authenticated else None
    
    context = {
        'subscription': user_subscription,
        'username': username,
    }
    return render(request, 'user/homeindex.html',context)  # Create a home.html template with a logout button


def cdata_view(request):
    persons = PersonData.objects.all()  # Fetch all PersonData entries
    return render(request, "cdata.html", {'persons': persons})







@login_required
def subscription_plans(request):
    plans = SubscriptionPlan.objects.all()
    username = request.user.username if request.user.is_authenticated else None
    return render(request, 'subscription_plans.html', {'plans': plans, 'username':username})

import paypalrestsdk
from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import SubscriptionPlan, UserSubscription

@login_required
def choose_plan(request, plan_id):
    username = request.user.username if request.user.is_authenticated else None
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    return render(request, 'payment.html', {'plan': plan , 'username':username})

@login_required
def process_payment(request):
    if request.method == 'POST':
        plan_id = request.POST.get('plan_id')
        plan = get_object_or_404(SubscriptionPlan, id=plan_id)

        # Configure PayPal SDK
        paypalrestsdk.configure({
            "mode": "sandbox",  # Use "live" in production
            "client_id": settings.PAYPAL_CLIENT_ID,
            "client_secret": settings.PAYPAL_CLIENT_SECRET
        })

        # Create the payment
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": request.build_absolute_uri(reverse('execute_payment')),  # Add this URL for execution
                "cancel_url": request.build_absolute_uri(reverse('subscription_plans'))  # Redirect to plans if canceled
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": plan.name,
                        "sku": str(plan.id),
                        "price": str(plan.price),
                        "currency": "USD",
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": str(plan.price),
                    "currency": "USD"
                },
                "description": f"Payment for {plan.name} subscription."
            }]
        })

        if payment.create():
            # Store payment ID in session to verify later
            request.session['payment_id'] = payment.id
            # Redirect to PayPal for payment approval
            for link in payment.links:
                if link.rel == "approval_url":
                    return redirect(link.href)
        else:
            # If payment creation fails
            return render(request, 'payment_error.html', {'error': payment.error})
from django.utils import timezone
from datetime import timedelta

@login_required
def execute_payment(request):
    # Retrieve the payment ID stored in session
    payment_id = request.session.get('payment_id')
    payer_id = request.GET.get('PayerID')

    if payment_id and payer_id:
        # Configure PayPal SDK
        paypalrestsdk.configure({
            "mode": "sandbox",  # Use "live" in production
            "client_id": settings.PAYPAL_CLIENT_ID,
            "client_secret": settings.PAYPAL_CLIENT_SECRET
        })

        # Find the payment object
        payment = paypalrestsdk.Payment.find(payment_id)

        # Execute the payment if it's approved
        if payment.execute({"payer_id": payer_id}):
            # Mark the subscription as purchased
            plan_id = payment.transactions[0].item_list.items[0].sku
            plan = get_object_or_404(SubscriptionPlan, id=plan_id)

            # Get or create the user's subscription and set expiration date
            user_subscription, created = UserSubscription.objects.update_or_create(
                user=request.user,
                defaults={'plan': plan}
            )

            # Set or update the expiration date
            if created or user_subscription.expiration_date < timezone.now():
                # If new or expired, set expiration to one month from now
                user_subscription.expiration_date = timezone.now() + timedelta(days=30)
            else:
                # Extend expiration date by one month if still active
                user_subscription.expiration_date += timedelta(days=30)

            user_subscription.save()

            # Clear the session payment ID after successful payment
            if 'payment_id' in request.session:
                del request.session['payment_id']

            return render(request, 'subscription_success.html', {'plan': plan})
        else:
            # Handle failed payment execution
            return render(request, 'payment_error.html', {'error': payment.error})
    else:
        # Redirect if payment ID or PayerID is missing
        return redirect('subscription_plans')

@login_required
def payment_success(request):
    # Get the user and the subscription plan
    user_subscription = UserSubscription.objects.get(user=request.user)

    # Save the user's subscription
    user_subscription.plan = user_subscription.plan  # Update the plan
    user_subscription.save()

    return render(request, 'subscription_success.html', {'plan': user_subscription.plan})

# @login_required
# def subscription_success(request):
#     return render(request, 'subscription_success.html')

# views.py

from django.shortcuts import render, redirect
from .models import UserProfile
from django.contrib.auth.decorators import login_required

@login_required
def subscription_success(request):
    if request.method == "POST":
        # Retrieve form data from POST request
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        profile_pic = request.FILES.get("profile_pic")
        country = request.POST.get("country")
        city = request.POST.get("city")
        zip_code = request.POST.get("zip_code")
        street = request.POST.get("street")

        # Update or create the user profile with the provided information
        profile, created = UserProfile.objects.update_or_create(
            user=request.user,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'profile_pic': profile_pic,
                'country': country,
                'city': city,
                'zip_code': zip_code,
                'street': street,
            }
        )

        # Redirect to a profile or success page after submitting the form
        return redirect('profile')  # Replace 'profile' with your actual success page URL

    # Render the form in the subscription success template
    return render(request, 'subscription_success.html')




@login_required
def plannotice(request):
    # Fetch the user's subscription
    try:
        subscription = UserSubscription.objects.get(user=request.user)
        expiration_date = subscription.expiration_date
    except UserSubscription.DoesNotExist:
        expiration_date = None  # Handle the case where there is no subscription

    return render(request, 'plannotice.html', {
        'username': request.user.username,  # Get the logged-in user's username
        'expiration_date': expiration_date,  # Get the expiration date
    })
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .models import UserSubscription

def check_subscription(view_func):
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        try:
            subscription = UserSubscription.objects.get(user=request.user)
            if not subscription.is_active():
                return redirect('plannotice')  # Redirect to the notice page if expired
        except UserSubscription.DoesNotExist:
            return redirect('plannotice')  # Redirect if no subscription exists
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view

@check_subscription
def homes(request):
    return render(request, 'all.html',)

from django.shortcuts import render

def testcase(request):
    # Get the username of the logged-in user
    username = request.user.username if request.user.is_authenticated else None
    return render(request, "base.html", {"username": username})

# views.py
from django.shortcuts import render, redirect
from .models import UserProfile
from django.contrib.auth.decorators import login_required

@login_required
def personal_details_plan(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        profile_pic = request.FILES.get('profile_pic')
        country = request.POST.get('country')
        city = request.POST.get('city')
        zip_code = request.POST.get('zip_code')
        street = request.POST.get('street')
        phone_number = request.POST.get('phone_number')

        # Create or update the user profile
        user_profile, created = UserProfile.objects.update_or_create(
            user=request.user,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'profile_pic': profile_pic,
                'country': country,
                'city': city,
                'zip_code': zip_code,
                'street': street,
                'phone_number': phone_number,
            }
        )

        return redirect('home')  # Redirect to the profile view

    return render(request, 'personal_details.html')  # Render the form template


# PAYMENT THING DONE UPSIDE NEXT FEATURE ----------------------------------------------------------------------------------------------------
# Working on user details My account featuere 

@login_required
def user_details(request):
    user_profile = UserProfile.objects.filter(user=request.user).first()
    user_subscription = UserSubscription.objects.filter(user=request.user).first()
    username = request.user.username if request.user.is_authenticated else None

    context = {
        'profile': user_profile,
        'subscription': user_subscription,
        'username': username,
        'user_email': request.user.email,
    }
    
    return render(request, 'user/user_details.html', context)


# from django.shortcuts import render, redirect
# from .models import PersonData, UserSearch
# from django.utils import timezone
# from datetime import timedelta

# def state_query(request):
#     # Check if the user has a valid previous search
#     user_search = UserSearch.objects.filter(user=request.user).first()
#     if user_search and user_search.is_valid():
#         # Redirect to results if a valid search exists within 30 days
#         return redirect('show_results')

#     # If POST request, save search and redirect
#     if request.method == 'POST':
#         state = request.POST.get('state', '').strip()
#         city = request.POST.get('city', '').strip()
#         zip_code = request.POST.get('zip_code', '').strip()

#         # Create or update the UserSearch entry
#         user_search, created = UserSearch.objects.update_or_create(
#             user=request.user,
#             defaults={'state': state, 'city': city, 'zip_code': zip_code, 'created_at': timezone.now()}
#         )

#         return redirect('show_results')

#     # Render the form initially
#     return render(request, 'user/state_query.html')

# def show_results(request):
#     # Retrieve the user's last search criteria
#     user_search = UserSearch.objects.filter(user=request.user).first()

#     if not user_search or not user_search.is_valid():
#         return redirect('state_query')  # Redirect if no valid search

#     # Filter PersonData based on search criteria
#     results = PersonData.objects.all()
#     if user_search.state:
#         results = results.filter(state__iexact=user_search.state)
#     if user_search.city:
#         results = results.filter(city__iexact=user_search.city)
#     if user_search.zip_code:
#         results = results.filter(zip_code__iexact=user_search.zip_code)

#     count = results.count()

#     return render(request, 'user/show_results.html', {
#         'results': results,
#         'count': count,
#         'user_search': user_search
#     })


# from django.shortcuts import render
# from .models import PersonData

# def state_data_detail(request, state):
#     # Fetch all records for the specified state
#     entries = PersonData.objects.filter(state__iexact=state)

#     context = {
#         'entries': entries,
#         'state': state,
#     }
#     return render(request, 'user/state_data_detail.html', context)


# views.py
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import PersonData, UserSearch
from django.contrib.auth.decorators import login_required
from django.db.models import Q

# views.py
from django.shortcuts import render
from django.utils import timezone
from .models import PersonData, UserSearch
from django.contrib.auth.decorators import login_required
from django.db.models import Q

@login_required
def search_person_data(request):
    user_search = UserSearch.objects.filter(user=request.user).first()  # Get the user's search

    # Check if a search was submitted
    if request.method == 'GET':
        state = request.GET.get('state', '')
        city = request.GET.get('city', '')
        zip_code = request.GET.get('zip_code', '')

        # If any search criteria is provided
        if state or city or zip_code:
            # Save the user's current search in UserSearch model
            user_search, created = UserSearch.objects.update_or_create(
                user=request.user,
                defaults={
                    'state': state,
                    'city': city,
                    'zip_code': zip_code,
                    'created_at': timezone.now()
                }
            )

    # Retrieve results based on the last search
    results = []
    if user_search:
        filters = Q()
        if user_search.state:
            filters |= Q(state__iexact=user_search.state)
        if user_search.city:
            filters |= Q(city__iexact=user_search.city)
        if user_search.zip_code:
            filters |= Q(zip_code=user_search.zip_code)

        results = PersonData.objects.filter(filters)
    username = request.user.username if request.user.is_authenticated else None
    return render(request, 'user/search.html', {
        'user_search': user_search,
        'results': results,
        'username':username,
    })



# views.py
from django.shortcuts import render
from django.utils import timezone
from .models import PersonData, UserSearch, UserContactAccess
from django.contrib.auth.decorators import login_required
from django.db.models import Q

@login_required
def search_person_data(request):
    user_search = UserSearch.objects.filter(user=request.user).first()  # Get the user's search

    # Check if a search was submitted
    if request.method == 'GET':
        state = request.GET.get('state', '')
        city = request.GET.get('city', '')
        zip_code = request.GET.get('zip_code', '')

        # If any search criteria is provided
        if state or city or zip_code:
            # Save the user's current search in UserSearch model
            user_search, created = UserSearch.objects.update_or_create(
                user=request.user,
                defaults={
                    'state': state,
                    'city': city,
                    'zip_code': zip_code,
                    'created_at': timezone.now()
                }
            )

            # Retrieve results based on the last search
            filters = Q()
            if state:
                filters |= Q(state__iexact=state)
            if city:
                filters |= Q(city__iexact=city)
            if zip_code:
                filters |= Q(zip_code=zip_code)

            results = PersonData.objects.filter(filters)

            ########
            user_profile = UserProfile.objects.filter(user=request.user).first()
            user_subscription = UserSubscription.objects.filter(user=request.user).first()
            username = request.user.username if request.user.is_authenticated else None

            context = {
                'profile': user_profile,
                'subscription': user_subscription,
                'username': username,
                'user_email': request.user.email,
            }
            if user_subscription and user_subscription.plan:
                accesscontacts = int(user_subscription.plan.contacts)
                print(f"Allowed contacts: {accesscontacts}")
            else:
                accesscontacts = 0
                print("No active subscription or plan.")
            ########

            # Count how many contacts the user has already accessed
            current_access_count = UserContactAccess.objects.filter(user=request.user).count()

            # Determine how many more contacts can be accessed
            available_slots = accesscontacts - current_access_count
            print(f"Current access count: {current_access_count}, Available slots: {available_slots}")

            # Save the results to UserContactAccess model, respecting the allowed limit
            for person in results:
                if available_slots > 0:
                    # Create an entry only if there are available slots
                    UserContactAccess.objects.get_or_create(
                        user=request.user,
                        person=person
                    )
                    available_slots -= 1  # Decrement available slots

            return render(request, 'user/search.html', {
                'user_search': user_search,
                'results': results,
            })

    # Default render if no search has been performed yet
    username = request.user.username if request.user.is_authenticated else None
    return render(request, 'user/search.html', {
        'username': username,
        'user_search': user_search,
        'results': []
    })


# # views.py
# from django.shortcuts import render
# from .models import UserContactAccess

# def accessed_contacts(request):
#     if request.user.is_authenticated:
#         contacts = UserContactAccess.objects.filter(user=request.user).select_related('person')
#     else:
#         contacts = []
#     username = request.user.username if request.user.is_authenticated else None
#     return render(request, 'user/accessed_contacts.html', {'contacts': contacts,'username':username})



from django.shortcuts import render
from .models import UserContactAccess

def accessed_contacts(request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Get search criteria from GET parameters
        search_query = request.GET.get('search', '')
        party_preference = request.GET.get('party_preference', '')

        # Filter contacts accessed by the user
        contacts = UserContactAccess.objects.filter(user=request.user).select_related('person')

        # Apply search filter
        if search_query:
            contacts = contacts.filter(person__first_name__icontains=search_query)

        # Apply party preference filter
        if party_preference:
            contacts = contacts.filter(person__party_preference__icontains=party_preference)
    else:
        contacts = []

    username = request.user.username if request.user.is_authenticated else None
    return render(request, 'user/accessed_contacts.html', {'contacts': contacts, 'username': username})


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import UserSubscription, UserContactAccess

@login_required
def add_contacts_view(request):
    if request.method == 'POST':
        try:
            # Get the user's subscription
            user_subscription = UserSubscription.objects.get(user=request.user)

            # Determine the number of allowed contacts based on the subscription plan
            if user_subscription.is_active():
                if user_subscription.plan.name.lower() == 'basic':
                    contacts_allowed = 20
                elif user_subscription.plan.name.lower() == 'team':
                    contacts_allowed = 30
                elif user_subscription.plan.name.lower() == 'organization':
                    contacts_allowed = 50
                else:
                    contacts_allowed = 0  # Default to 0 if the plan is unrecognized

                # Create or update UserContactAccess record
                UserContactAccess.objects.update_or_create(
                    user=request.user,
                    defaults={'contacts_allowed': contacts_allowed}
                )

                # Redirect or return a success response
                return redirect('home')  # Replace with your success page
            else:
                return render(request, 'user/error.html', {'message': 'Subscription is not active.'})
        except UserSubscription.DoesNotExist:
            return render(request, 'user/error.html', {'message': 'User subscription does not exist.'})

    # If not a POST request, render the form page
    username = request.user.username if request.user.is_authenticated else None
    return render(request, 'user/add_contacts.html',{'username':username})  # Replace with your actual template




# def poltaker_page(request):
#     return render(request,"user/poltakers.html")


# views.py

# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Poltaker
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Poltaker  # Ensure Poltaker model is imported

from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .models import Poltaker, UserSubscription

@login_required
def add_poltaker(request):
    can_add_poltaker = True  # Default assumption

    # Handle form submission
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        zip_code = request.POST.get('zip_code')
        password = request.POST.get('password')
        mobile = request.POST.get('mobile')

        if name and email and zip_code and password:
            try:
                user_subscription = UserSubscription.objects.get(user=request.user)

                if user_subscription.is_active():
                    # Determine the number of allowed contacts based on the subscription plan
                    if user_subscription.plan.name.lower() == 'basic':
                        poltakers_allowed = 1
                    elif user_subscription.plan.name.lower() == 'team':
                        poltakers_allowed = 10
                    elif user_subscription.plan.name.lower() == 'organization':
                        poltakers_allowed = 999
                    else:
                        poltakers_allowed = 0

                    poltakers_count = Poltaker.objects.filter(user=request.user).count()

                    if poltakers_count >= poltakers_allowed:
                        messages.error(request, 'Maximum allowed Poltakers exceeded. Please upgrade your subscription or remove some Poltakers , or You can just carry on with how many poltakers you have ')
                        can_add_poltaker = False
                        return render(request, 'user/add_poltaker.html', {
                            'poltakers': Poltaker.objects.filter(user=request.user),
                            'can_add_poltaker': can_add_poltaker,
                        })

                # Create the Poltaker if the limit has not been exceeded
                Poltaker.objects.create(
                    user=request.user,
                    name=name,
                    email=email,
                    zip_code=zip_code,
                    password=password
                )
                messages.success(request, f'Poltaker "{name}" added successfully!')
                return redirect('add_poltaker')

            except UserSubscription.DoesNotExist:
                messages.error(request, 'User subscription not found. Please contact support.')
                can_add_poltaker = False
                return render(request, 'user/add_poltaker.html', {
                    'poltakers': Poltaker.objects.filter(user=request.user),
                    'can_add_poltaker': can_add_poltaker,
                })
        else:
            messages.error(request, 'Please fill in all fields.')

    # Fetch all poltakers created by the current user
    poltakers = Poltaker.objects.filter(user=request.user)
    username = request.user.username if request.user.is_authenticated else None
    return render(request, 'user/add_poltaker.html', {
        'poltakers': poltakers,
        'can_add_poltaker': can_add_poltaker,
        'username': username,
    })

# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.hashers import check_password
from .models import Poltaker

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Poltaker

def poltaker_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            poltaker = Poltaker.objects.get(email=email, password=password)
            request.session['poltaker_id'] = poltaker.id
            return redirect('poltaker_dashboard')  # Ensure this URL name is correct
        except Poltaker.DoesNotExist:
            messages.error(request, 'Invalid email or password.')
    return render(request, 'poltaker/login.html')

from django.shortcuts import render, redirect

def poltaker_dashboard(request):
    if 'poltaker_id' not in request.session:
        return redirect('poltaker_login')  # Redirect to login if not authenticated

    poltaker = Poltaker.objects.get(id=request.session['poltaker_id'])
    context = {'poltaker': poltaker}
    return render(request, 'poltaker/dashboard.html', context)

from django.shortcuts import redirect

def poltaker_logout(request):
    if 'poltaker_id' in request.session:
        del request.session['poltaker_id']  # Remove poltaker session
    return redirect('poltaker_login')  # Redirect to the login page

# Now Adding question feature 
from django.shortcuts import render, redirect
from .models import Question, Option
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Question, Option


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Question, Option

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages  # Import messages framework
from .models import Question, Option

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages  # Import messages framework
from .models import Question, Option

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages  # Import messages framework
from .models import Question, Option

from django.contrib import messages
from django.shortcuts import redirect, render

@login_required
def add_questions(request):
    if request.method == 'POST':
        question_text = request.POST.get('question_text')
        options = request.POST.getlist('options')

        # Validate that a question and at least one option is provided
        if not question_text or not options:
            messages.error(request, "Please provide a question and at least one option.")
            return redirect('add_questions')  # Redirect to the same page
        
        # Create the question
        question = Question.objects.create(user=request.user, question_text=question_text)

        # Create options if they exist
        for option_text in options:
            if option_text:
                Option.objects.create(question=question, option_text=option_text)

        messages.success(request, "Question added successfully!")  # Add a success message
        return redirect('add_questions')  # Redirect to the same page after saving
    username = request.user.username if request.user.is_authenticated else None
    return render(request, 'questions/add_questions.html',{'username':username})

@login_required
def view_questions(request):
    # Retrieve questions for the logged-in user
    questions = Question.objects.filter(user=request.user)
    username = request.user.username if request.user.is_authenticated else None

    return render(request, 'questions/view_questions.html', {'questions': questions,'username':username})





# Working on survey --------------------------------------------------------------------
def survey_work(request):
    return render(request , 'survey/survey.html')