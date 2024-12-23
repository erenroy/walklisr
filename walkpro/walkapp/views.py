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

import random
import smtplib
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.cache import cache

def first_look(request):
    plans = SubscriptionPlan.objects.all()  # Fetch all subscription plans
    return render(request, 'look/index.html', {'plans': plans})  # Pass plans to the template

from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.cache import cache
import random

def send_otp(email, otp):
    subject = "Your OTP Code"
    message = f"Your OTP code is {otp}. Please use this to complete your registration."
    sender_email = "criscallion@gmail.com"
    app_password = "gdpi idvs coiy fgdm"
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.sendmail(sender_email, email, f"Subject: {subject}\n\n{message}")
        server.quit()
    except Exception as e:
        print(f"Error sending email: {str(e)}")

def generate_otp():
    return random.randint(100000, 999999)

def register(request):
    if request.method == 'POST':
        username = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if username and email and password:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists. Please use different credentials.')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email is already registered. Please use different credentials.')
            else:
                try:
                    otp = generate_otp()
                    cache.set(email, otp, timeout=300)  # Store OTP in cache for 5 minutes
                    send_otp(email, otp)
                    request.session['username'] = username
                    request.session['email'] = email
                    request.session['password'] = password
                    return redirect('verify_otp')
                except Exception as e:
                    messages.error(request, f'Error creating account: {str(e)}')
        else:
            messages.error(request, 'Please fill in all fields.')
    return render(request, 'register.html')

def verify_otp(request):
    if request.method == 'POST':
        email = request.session.get('email')
        otp = request.POST.get('otp')
        cached_otp = cache.get(email)
        
        if str(cached_otp) == otp:
            username = request.session.get('username')
            password = request.session.get('password')
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
            return redirect('verify_otp')
    
    return render(request, 'verify_otp.html')

# walkapp/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib import messages
from .models import UserSubscription
from walkapp.models import Poltaker
User = get_user_model()

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Attempt User login
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)  # Log in the user

                # Check User's subscription status
                if UserSubscription.objects.filter(user=user).exists():
                    return redirect('home')  # Redirect to home page
                else:
                    return redirect('subscription_plans')  # Redirect to subscription plans
            else:
                messages.error(request, 'Invalid email or password for user.')
                return render(request, 'login.html')  # Reload login page with error
        except User.DoesNotExist:
            pass  # Continue to check for Poltaker

        # Attempt Poltaker login
        try:
            poltaker = Poltaker.objects.get(email=email)
            if poltaker.password == password:  # Plain text comparison
                # Set session for Poltaker
                request.session['poltaker_id'] = poltaker.id

                # Check if Poltaker needs to change password
                if not poltaker.password_changed:
                    return redirect('surveyapp:password_change')  # Redirect to password change page

                return redirect('surveyapp:poltaker_dashboard')  # Redirect to Poltaker dashboard
            else:
                messages.error(request, 'Invalid password for Poltaker.')
                return render(request, 'login.html')  # Reload login page with error
        except Poltaker.DoesNotExist:
            pass  # No match for Poltaker either

        # If neither User nor Poltaker credentials match, show error
        messages.error(request, 'Invalid email or password.')
        return render(request, 'login.html')

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('first_look')
# Login , Register end here ------------------------------------------------------------------------------------------------------------------------

from surveyapp.models import Survey

# Dashboard view starts here -------------------------------------------------------------------------------------------------------------


@login_required
def home_view(request):
    # Fetch user-related data
    user_subscription = UserSubscription.objects.filter(user=request.user).first()
    username = request.user.username if request.user.is_authenticated else None
    user_profile = UserProfile.objects.filter(user=request.user).first()

    # Ensure the user is logged in and filter surveys based on user (created_by)
    surveys = Survey.objects.filter(created_by=request.user)

    # Manually filter surveys by unique survey_token
    seen_tokens = set()
    unique_surveys = []

    # Loop through the surveys and ensure only one survey per survey_token is added
    for survey in surveys:
        if survey.survey_token not in seen_tokens:
            unique_surveys.append(survey)
            seen_tokens.add(survey.survey_token)

    # Prepare data for the last 7 days
    today = timezone.now()
    last_7_days = [today - timedelta(days=i) for i in range(7)]  # Get last 7 days

    successful_data = []
    in_progress_data = []
    denied_data = []
    survey_labels = [day.strftime('%b %d') for day in last_7_days]  # Labels for the days

    # Loop through the last 7 days and count unique surveys for each status
    for day in last_7_days:
        successful_count_day = 0
        in_progress_count_day = 0
        denied_count_day = 0

        for token in seen_tokens:
            # Get all surveys for the current token
            related_surveys = Survey.objects.filter(survey_token=token)

            # Check the statuses of the related surveys
            completed_count = related_surveys.filter(status='completed', created_at__date=day.date()).count()
            in_progress_count = related_surveys.filter(status='pending', created_at__date=day.date()).count()
            pending_count = related_surveys.filter(status='in_progress', created_at__date=day.date()).count()

            if completed_count == related_surveys.count():
                successful_count_day += 1
            elif in_progress_count > 0:
                in_progress_count_day += 1
            elif pending_count > 0:
                denied_count_day += 1

        successful_data.append(successful_count_day)
        in_progress_data.append(in_progress_count_day)
        denied_data.append(denied_count_day)
    
    user = request.user
    denial_count = SurveyResponse.objects.filter(polltaker__user=user, denial_reason__isnull=False).count()
    context = {
        'subscription': user_subscription,
        'username': username,
        'surveys': unique_surveys,
        'profile': user_profile,
        'user_email': request.user.email,
        'successful_count': sum(successful_data),
        'in_progress_count': sum(in_progress_data),
        'denied_count': sum(denied_data),
        # Data for the last 7 days' chart
        'successful_data': successful_data,
        'in_progress_data': in_progress_data,
        'denied_data': denied_data,
        'survey_labels': survey_labels,
        'denial_count': denial_count
    }

    return render(request, 'user/homeindex.html', context)  # Render template with updated context
# Dashboard view Ends here -------------------------------------------------------------------------------------------------------------



def cdata_view(request):
    persons = PersonData.objects.all()  # Fetch all PersonData entries
    return render(request, "cdata.html", {'persons': persons})




# PAYMENT SUSCRIPTION view Ends here -------------------------------------------------------------------------------------------------------------



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

from paymentinfo.models import PaymentConfig
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
import stripe



@login_required
def process_payment(request):
    if request.method == 'POST':
        plan_id = request.POST.get('plan_id')
        plan = get_object_or_404(SubscriptionPlan, id=plan_id)

        # Fetch PaymentConfig (for both payment method and credentials)
        payment_config = PaymentConfig.objects.first()

        if not payment_config:
            # Handle the case where no PaymentConfig is found
            return render(request, 'payment_error.html', {'error': 'Payment configuration not found in the database.'})

        payment_method = payment_config.payment_method  # This field should be either 'paypal' or 'stripe'
        
        if payment_method == 'paypal':
            # PayPal payment flow
            client_id = payment_config.client_id
            client_secret = payment_config.client_secret

            # Configure PayPal SDK with the credentials
            paypalrestsdk.configure({
                "mode": "sandbox",  # Use "live" in production
                "client_id": client_id,
                "client_secret": client_secret
            })

            # Calculate annual price
            annual_price = plan.price * 12

            # Create the PayPal payment
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
                            "price": str(annual_price),
                            "currency": "USD",
                            "quantity": 1
                        }]
                    },
                    "amount": {
                        "total": str(annual_price),
                        "currency": "USD"
                    },
                    "description": f"Payment for {plan.name} annual subscription."
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
                # If payment creation fails, show error
                return render(request, 'payment_error.html', {'error': payment.error})

        elif payment_method == 'stripe':
            # Stripe payment flow
            stripe.api_key = payment_config.stripe_secret_key  # Use the Stripe Secret Key from PaymentConfig

            # Calculate annual price
            annual_price = plan.price * 12

            try:
                # Create a Stripe Checkout session
                session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[
                        {
                            'price_data': {
                                'currency': 'usd',
                                'product_data': {
                                    'name': plan.name,
                                },
                                'unit_amount': int(annual_price * 100),  # Stripe expects the amount in cents
                            },
                            'quantity': 1,
                        },
                    ],
                    mode='payment',
                    success_url=request.build_absolute_uri(reverse('execute_payment')) + "?session_id={CHECKOUT_SESSION_ID}",
                    cancel_url=request.build_absolute_uri(reverse('subscription_plans')),
                    metadata={
                        'plan_id': plan.id,  # Add the plan_id here for later use
                    }
                )
                # Store session ID in the session for later use
                request.session['stripe_session_id'] = session.id
                # Redirect to Stripe Checkout
                return redirect(session.url)
            except stripe.error.StripeError as e:
                return render(request, 'payment_error.html', {'error': str(e)})

        else:
            # Handle case where neither PayPal nor Stripe is set
            return render(request, 'payment_error.html', {'error': 'No valid payment method selected.'})

@login_required
def execute_payment(request):
    # Retrieve the payment ID stored in session for PayPal (same as before)
    payment_id = request.session.get('payment_id')
    payer_id = request.GET.get('PayerID')

    if payment_id and payer_id:
        # Fetch PayPal credentials from the PaymentConfig model
        payment_config = PaymentConfig.objects.first()

        if not payment_config:
            return render(request, 'payment_error.html', {'error': 'PayPal credentials not found in the database.'})

        client_id = payment_config.client_id
        client_secret = payment_config.client_secret

        # Configure PayPal SDK with the credentials
        paypalrestsdk.configure({
            "mode": "sandbox",  # Use "live" in production
            "client_id": client_id,
            "client_secret": client_secret
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
                # If new or expired, set expiration to one year from now
                user_subscription.expiration_date = timezone.now() + timedelta(days=365)
            else:
                # Extend expiration date by one year if still active
                user_subscription.expiration_date += timedelta(days=365)

            user_subscription.save()

            # Clear the session payment ID after successful payment
            if 'payment_id' in request.session:
                del request.session['payment_id']

            return render(request, 'subscription_success.html', {'plan': plan})
        else:
            # Handle failed payment execution
            return render(request, 'payment_error.html', {'error': payment.error})

    # Now, handle Stripe payment execution
    stripe_session_id = request.GET.get('session_id')
    if stripe_session_id:
        # Fetch Stripe session ID from session if available
        session_id = request.session.get('stripe_session_id')

        if session_id == stripe_session_id:
            try:
                # Retrieve Stripe session object
                session = stripe.checkout.Session.retrieve(session_id)

                if session.payment_status == 'paid':
                    # Get plan ID from the metadata
                    plan_id = session.metadata.get('plan_id')  # Retrieve plan_id from metadata
                    if not plan_id:
                        raise KeyError("Plan ID is missing in the session metadata.")

                    # Get the plan object using the plan_id
                    plan = get_object_or_404(SubscriptionPlan, id=plan_id)

                    # Get or create the user's subscription and set expiration date
                    user_subscription, created = UserSubscription.objects.update_or_create(
                        user=request.user,
                        defaults={'plan': plan}
                    )

                    # Set or update the expiration date
                    if created or user_subscription.expiration_date < timezone.now():
                        # If new or expired, set expiration to one year from now
                        user_subscription.expiration_date = timezone.now() + timedelta(days=365)
                    else:
                        # Extend expiration date by one year if still active
                        user_subscription.expiration_date += timedelta(days=365)

                    user_subscription.save()

                    # Clear the session session ID after successful payment
                    if 'stripe_session_id' in request.session:
                        del request.session['stripe_session_id']

                    return render(request, 'subscription_success.html', {'plan': plan})

                else:
                    return render(request, 'payment_error.html', {'error': 'Payment not successful with Stripe.'})

            except stripe.error.StripeError as e:
                return render(request, 'payment_error.html', {'error': str(e)})

    return redirect('subscription_plans')

@login_required
def payment_success(request):
    # Get the user and the subscription plan
    user_subscription = UserSubscription.objects.get(user=request.user)

    # Save the user's subscription
    user_subscription.plan = user_subscription.plan  # Update the plan (no change needed here)
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
# PAYMENT SUSCRIPTION view Ends here -------------------------------------------------------------------------------------------------------------

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

from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Poltaker, UserSubscription
from .utils import send_poltaker_email  # Import the email sending function

# @login_required
# def add_poltaker(request):
#     can_add_poltaker = True  # Default assumption

#     # Handle form submission
#     if request.method == 'POST':
#         name = request.POST.get('name')
#         email = request.POST.get('email')
#         zip_code = request.POST.get('zip_code')
#         password = request.POST.get('password')
#         mobile = request.POST.get('mobile')

#         if name and email and zip_code and password:
#             try:
#                 user_subscription = UserSubscription.objects.get(user=request.user)

#                 if user_subscription.is_active():
#                     # Determine the number of allowed contacts based on the subscription plan
#                     if user_subscription.plan.name.lower() == 'basic':
#                         poltakers_allowed = 1
#                     elif user_subscription.plan.name.lower() == 'team':
#                         poltakers_allowed = 10
#                     elif user_subscription.plan.name.lower() == 'organization':
#                         poltakers_allowed = 999
#                     else:
#                         poltakers_allowed = 0

#                     poltakers_count = Poltaker.objects.filter(user=request.user).count()

#                     if poltakers_count >= poltakers_allowed:
#                         messages.error(request, 'Maximum allowed Poltakers exceeded. Please upgrade your subscription or remove some Poltakers, or you can just carry on with how many Poltakers you have.')
#                         can_add_poltaker = False
#                         return render(request, 'user/add_poltaker.html', {
#                             'poltakers': Poltaker.objects.filter(user=request.user),
#                             'can_add_poltaker': can_add_poltaker,
#                         })

#                 # Create the Poltaker if the limit has not been exceeded
#                 poltaker = Poltaker.objects.create(
#                     user=request.user,
#                     name=name,
#                     email=email,
#                     zip_code=zip_code,
#                     password=password,
#                     mobile=mobile,
#                 )
#                 # Send email notification to the new Poltaker
#                 send_poltaker_email(poltaker)

#                 messages.success(request, f'Poltaker "{name}" added successfully!')
#                 return redirect('add_poltaker')

#             except IntegrityError:
#                 messages.error(request, f'A Poltaker with the email "{email}" already exists. Please use a different email address.')
#             except UserSubscription.DoesNotExist:
#                 messages.error(request, 'User subscription not found. Please contact support.')
#                 can_add_poltaker = False
#                 return render(request, 'user/add_poltaker.html', {
#                     'poltakers': Poltaker.objects.filter(user=request.user),
#                     'can_add_poltaker': can_add_poltaker,
#                 })
#         else:
#             messages.error(request, 'Please fill in all fields.')

#     # Fetch all poltakers created by the current user
#     poltakers = Poltaker.objects.filter(user=request.user)
#     username = request.user.username if request.user.is_authenticated else None
#     return render(request, 'user/add_poltaker.html', {
#         'poltakers': poltakers,
#         'can_add_poltaker': can_add_poltaker,
#         'username': username,
#     })
import csv
import io
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from .models import Poltaker, UserSubscription
from .utils import send_poltaker_email  # Assuming you have this utility function


@login_required
def add_poltaker(request):
    can_add_poltaker = True  # Default assumption
    
    if request.method == 'POST':
        # Handle CSV file upload
        if 'csv_file' in request.FILES:
            csv_file = request.FILES['csv_file']
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'Please upload a valid CSV file.')
                return redirect('add_poltaker')

            try:
                # Read and parse the CSV file
                data_set = csv_file.read().decode('UTF-8')
                io_string = io.StringIO(data_set)
                next(io_string)  # Skip the header row
                
                for row in csv.reader(io_string, delimiter=','):
                    name, email, zip_code, password, mobile = row
                    if name and email and zip_code and password:
                        handle_poltaker_creation(request.user, name, email, zip_code, password, mobile)
                
                messages.success(request, 'Poltakers added successfully from CSV.')
                return redirect('add_poltaker')

            except Exception as e:
                messages.error(request, f"Error processing CSV: {e}")
                return redirect('add_poltaker')

        # Handle manual poltaker form submission
        else:
            name = request.POST.get('name')
            email = request.POST.get('email')
            zip_code = request.POST.get('zip_code')
            password = request.POST.get('password')
            mobile = request.POST.get('mobile')

            if name and email and zip_code and password:
                try:
                    handle_poltaker_creation(request.user, name, email, zip_code, password, mobile)
                    messages.success(request, f'Poltaker "{name}" added successfully!')
                    return redirect('add_poltaker')
                except IntegrityError:
                    messages.error(request, f'A Poltaker with the email "{email}" already exists.')
                except UserSubscription.DoesNotExist:
                    messages.error(request, 'User subscription not found. Please contact support.')

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


def handle_poltaker_creation(user, name, email, zip_code, password, mobile):
    # Check user's subscription plan to ensure they can add more poltakers
    user_subscription = UserSubscription.objects.get(user=user)

    if user_subscription.is_active():
        # Define poltaker limits based on the user's subscription plan
        plan = user_subscription.plan.name.lower()
        poltakers_allowed = 0
        if plan == 'basic':
            poltakers_allowed = 1
        elif plan == 'team':
            poltakers_allowed = 10
        elif plan == 'organization':
            poltakers_allowed = 999

        poltakers_count = Poltaker.objects.filter(user=user).count()

        if poltakers_count >= poltakers_allowed:
            raise ValueError('Maximum allowed Poltakers exceeded. Please upgrade your subscription or remove some Poltakers.')

    # Create the new poltaker
    poltaker = Poltaker.objects.create(
        user=user,
        name=name,
        email=email,
        zip_code=zip_code,
        password=password,
        mobile=mobile,
    )

    # Send email notification to the new Poltaker
    send_poltaker_email(poltaker)
# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.hashers import check_password
from .models import Poltaker

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Poltaker
# views.py
# Polltaker starts here --------- no use - poltaker view has changed ------------------------------------------------------------
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

            # Check if the poltaker needs to change their password
            if poltaker.password_changed is False:
                return redirect('poltaker_change_password')  # Redirect to change password

            return redirect('poltaker_dashboard')  # Redirect to dashboard if password is already changed
        except Poltaker.DoesNotExist:
            messages.error(request, 'Invalid email or password.')
    return render(request, 'poltaker/login.html')


def poltaker_dashboard(request):
    if 'poltaker_id' not in request.session:
        return redirect('poltaker_login')  # Redirect to login if not authenticated

    poltaker = Poltaker.objects.get(id=request.session['poltaker_id'])
    context = {'poltaker': poltaker}
    return render(request, 'poltaker/dashboard.html', context)


def poltaker_change_password(request):
    if 'poltaker_id' not in request.session:
        return redirect('poltaker_login')  # Redirect to login if not authenticated

    poltaker = Poltaker.objects.get(id=request.session['poltaker_id'])

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password and new_password == confirm_password:
            # Update the password and mark it as changed
            poltaker.password = new_password
            poltaker.password_changed = True  # Ensure to add this field in your Poltaker model
            poltaker.save()
            messages.success(request, 'Your password has been changed successfully!')
            return redirect('poltaker_dashboard')  # Redirect to dashboard after changing password
        else:
            messages.error(request, 'Passwords do not match or are empty.')

    return render(request, 'poltaker/change_password.html')


def poltaker_logout(request):
    if 'poltaker_id' in request.session:
        del request.session['poltaker_id']  # Remove poltaker session
    return redirect('poltaker_login')  # Redirect to the login page
# Polltaker Ends here --------- no use - poltaker view has changed ------------------------------------------------------------

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

from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .models import Question, Option

import csv
from django.core.files.storage import FileSystemStorage

@login_required
def add_questions(request):
    if request.method == 'POST':
        # Check if a CSV file is uploaded
        if 'csv_file' in request.FILES:
            csv_file = request.FILES['csv_file']
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'Please upload a CSV file.')
                return redirect('add_questions')

            # Save the uploaded file
            fs = FileSystemStorage()
            filename = fs.save(csv_file.name, csv_file)
            file_path = fs.path(filename)

            # Parse the CSV file with a different encoding to avoid UnicodeDecodeError
            try:
                with open(file_path, newline='', encoding='ISO-8859-1') as csvfile:
                    reader = csv.reader(csvfile)
                    next(reader)  # Skip the header row
                    for row in reader:
                        question_text, question_type, *options = row
                        if not question_text or not question_type:
                            continue  # Skip incomplete rows

                        question = Question.objects.create(user=request.user, question_text=question_text, question_type=question_type)

                        if question_type == 'mcq' and options:
                            for option_text in options:
                                if option_text:
                                    Option.objects.create(question=question, option_text=option_text)

                messages.success(request, 'Questions added successfully from CSV!')
                return redirect('view_questions')

            except UnicodeDecodeError as e:
                messages.error(request, f"Error reading CSV file: {e}")
                return redirect('view_questions')

        # Handle manual question form submission
        question_text = request.POST.get('question_text')
        question_type = request.POST.get('question_type')
        options = request.POST.getlist('options')

        if not question_text or not question_type:
            messages.error(request, 'Please provide a question and select a question type.')
            return redirect('add_questions')

        question = Question.objects.create(user=request.user, question_text=question_text, question_type=question_type)

        for option_text in options:
            if option_text:
                Option.objects.create(question=question, option_text=option_text)

        messages.success(request, 'Question added successfully!')
        return redirect('view_questions')

    username = request.user.username if request.user.is_authenticated else None
    return render(request, 'questions/add_questions.html', {'username': username})



from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Question  # Adjust the import as needed based on your project structure
from .models import GeneralQuestion


@login_required
def view_questions(request):
    """
    View to display questions created by the logged-in user.
    Only authenticated users can access this view.
    """
    # Retrieve questions for the logged-in user
    questions = Question.objects.filter(user=request.user)

    # Get the username of the logged-in user
    username = request.user.username if request.user.is_authenticated else None
    general_questions = GeneralQuestion.objects.all()  # Retrieve all GeneralQuestion instances

    # Render the questions in the 'view_questions.html' template
    return render(request, 'questions/view_questions.html', {
        'questions': questions,
        'username': username,
        # 'general_questions': general_questions,
    })


from django.shortcuts import render
from django.db.models import Q
from .models import Question, GeneralQuestion

@login_required
def question_search(request):
    query = request.GET.get('q', '')
    
    # Search in both models
    user_questions = Question.objects.filter(Q(question_text__icontains=query) & Q(user=request.user))
    general_questions = GeneralQuestion.objects.filter(question_text__icontains=query)

    # Combine results into a single list
    combined_questions = list(user_questions) + list(general_questions)

    return render(request, 'questions/question_search.html', {
        'questions': combined_questions,
        'query': query,
    })


# Working on survey ---------------------------------------------------------------------------------------------------------
def survey_work(request):
    return render(request , 'survey/survey.html')





# Ending of survey -----------------------------------------------------------------------------------------------------------

# Forget password Feature start ----------------------------------------------------------------------------------------------
# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import EmailMessage
from django.urls import reverse
from django.utils import timezone
from .models import PasswordReset
from django.conf import settings

def ForgotPassword(request):
    if request.method == "POST":
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)

            new_password_reset = PasswordReset(user=user)
            new_password_reset.save()

            password_reset_url = reverse('reset-password', kwargs={'reset_id': new_password_reset.reset_id})

            full_password_reset_url = f'{request.scheme}://{request.get_host()}{password_reset_url}'

            email_body = f'Reset your password using the link below:\n\n{full_password_reset_url}'
        
            email_message = EmailMessage(
                'Reset your password',  # email subject
                email_body,
                settings.EMAIL_HOST_USER,  # email sender
                [email]  # email receiver
            )

            email_message.fail_silently = False
            email_message.send()

            return redirect('password-reset-sent', reset_id=new_password_reset.reset_id)

        except User.DoesNotExist:
            messages.error(request, f"No user with email '{email}' found")
            return redirect('forgot-password')

    return render(request, 'forgot_password.html')

def PasswordResetSent(request, reset_id):
    if PasswordReset.objects.filter(reset_id=reset_id).exists():
        return render(request, 'password_reset_sent.html')
    else:
        messages.error(request, 'Invalid reset id')
        return redirect('forgot-password')

def ResetPassword(request, reset_id):
    try:
        password_reset_id = PasswordReset.objects.get(reset_id=reset_id)

        if request.method == "POST":
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            passwords_have_error = False

            if password != confirm_password:
                passwords_have_error = True
                messages.error(request, 'Passwords do not match')

            if len(password) < 5:
                passwords_have_error = True
                messages.error(request, 'Password must be at least 5 characters long')

            expiration_time = password_reset_id.created_when + timezone.timedelta(minutes=10)

            if timezone.now() > expiration_time:
                passwords_have_error = True
                messages.error(request, 'Reset link has expired')

                password_reset_id.delete()

            if not passwords_have_error:
                user = password_reset_id.user
                user.set_password(password)
                user.save()

                password_reset_id.delete()

                messages.success(request, 'Password reset. Proceed to login')
                return redirect('login')
            else:
                return redirect('reset-password', reset_id=reset_id)

    except PasswordReset.DoesNotExist:
        messages.error(request, 'Invalid reset id')
        return redirect('forgot-password')

    return render(request, 'reset_password.html')
# Forget password Feature End ------------------------------------------------------------------------------------







# views.py
# from django.shortcuts import render
# from .models import GeneralQuestion

# def test_model_questions(request):
#     general_questions = GeneralQuestion.objects.all()  # Retrieve all GeneralQuestion instances
#     return render(request, 'testmodelq.html', {'general_questions': general_questions})


# Adding contact list feature start here ---------------------------------------------------------------------------------------
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
import csv
from .models import UserContactList

# views.py

from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import UserContactList
import csv
from django.contrib.auth.decorators import login_required
# views.py

from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import UserContactList
import csv
import io
from django.contrib.auth.decorators import login_required
import csv
import io
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import UserContactList

import csv
import io
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import UserContactList

import csv
import io
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import UserContactList

import csv
import io
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from .models import UserContactList

@login_required
def upload_contacts(request):
    if request.method == 'POST':
        if request.FILES.get('contact_file'):
            file = request.FILES['contact_file']
            decoded_file = file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            csv_reader = csv.reader(io_string, delimiter=',')
            next(csv_reader)  # Skip the header row

            contacts = []
            for row in csv_reader:
                try:
                    dob = row[11] if len(row) > 11 else None
                    reg_date = row[12] if len(row) > 12 else None

                    # Convert dates to YYYY-MM-DD format
                    if dob:
                        dob = datetime.strptime(dob, '%m/%d/%Y').strftime('%Y-%m-%d')
                    if reg_date:
                        reg_date = datetime.strptime(reg_date, '%m/%d/%Y').strftime('%Y-%m-%d')

                    contacts.append(UserContactList(
                        user=request.user,
                        first_name=row[3] if len(row) > 3 else 'NA',  # FNAME
                        last_name=row[2] if len(row) > 2 else 'NA',   # LNAME
                        email=row[19] if len(row) > 19 else 'NA',     # EMAIL
                        street=row[6] if len(row) > 6 else 'NA',      # ADDRESS
                        city=row[7] if len(row) > 7 else 'NA',        # CITY
                        state=row[8] if len(row) > 8 else 'NA',       # STATE
                        country='NA',  # Default to 'NA' since it is not in CSV
                        zipcode=row[9] if len(row) > 9 else 'NA',     # ZIP
                        party_preference='NA',  # Default to 'NA' since it is not in CSV
                        state_id=row[0] if len(row) > 0 else 'NA',    # STATE_ID
                        voter_nbr=row[1] if len(row) > 1 else 'NA',   # VOTER_NBR
                        title=row[4] if len(row) > 4 else 'NA',       # TITLE
                        address=row[5] if len(row) > 5 else 'NA',     # ADDRESS2
                        address2=row[6] if len(row) > 6 else 'NA',    # ADDRESS2
                        phone=row[10] if len(row) > 10 else 'NA',     # PHONE
                        dob=dob,       # DOB
                        reg_date=reg_date,  # REG_DATE
                        district=row[13] if len(row) > 13 else 'NA',  # DISTRICT
                        pct_nbr=row[14] if len(row) > 14 else 'NA',   # PCT_NBR
                        ward=row[15] if len(row) > 15 else 'NA',      # WARD
                    ))
                except ValueError as e:
                    print(f"Error parsing row: {row} - {e}")
                    continue  # Skip this row and proceed with the next one

            UserContactList.objects.bulk_create(contacts)

            return redirect('contacts_list')  # Redirect to a page that lists contacts

        elif 'manual_entry' in request.POST:
            UserContactList.objects.create(
                user=request.user,
                first_name=request.POST['first_name'],
                last_name=request.POST['last_name'],
                email=request.POST['email'],
                street=request.POST['street'],
                city=request.POST['city'],
                state=request.POST['state'],
                country=request.POST['country'],
                zipcode=request.POST['zipcode'],
                party_preference=request.POST.get('party_preference', 'NA'),
                state_id=request.POST.get('state_id', 'NA'),
                voter_nbr=request.POST.get('voter_nbr', 'NA'),
                title=request.POST.get('title', 'NA'),
                address=request.POST.get('address', 'NA'),
                address2=request.POST.get('address2', 'NA'),
                phone=request.POST.get('phone', 'NA'),
                dob=request.POST.get('dob', None),
                reg_date=request.POST.get('reg_date', None),
                district=request.POST.get('district', 'NA'),
                pct_nbr=request.POST.get('pct_nbr', 'NA'),
                ward=request.POST.get('ward', 'NA'),
            )
            return redirect('contacts_list')  # Redirect to a page that lists contacts

    username = request.user.username
    return render(request, 'contactlists/upload_contacts.html', {'username': username})

# views.py

from django.shortcuts import render, get_object_or_404
from .models import UserContactList, UserSubscription

# views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import UserContactList, UserSubscription

from django.db.models import Prefetch

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@login_required
def contact_list(request):
    # Fetch user subscription and contacts limit
    user_subscription = get_object_or_404(UserSubscription, user=request.user)
    contacts_limit = user_subscription.plan.contacts  # Ensure this attribute exists

    # Optimize query by limiting contacts directly in the query and using prefetch_related if needed
    user_contacts = UserContactList.objects.filter(user=request.user)[:contacts_limit]  # Limit contacts in the query itself

    # Pagination settings
    page = request.GET.get('page', 1)
    paginator = Paginator(user_contacts, 20)  # Show 20 contacts per page

    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)

    # Pass contacts and username to the template
    username = request.user.username

    # Print the contacts limit to the terminal
    print(f"User {request.user.username} can see up to {contacts_limit} contacts.")

    return render(request, 'contactlists/contact_list.html', {'contacts': contacts, 'username': username})


@login_required
def delete_contacts(request):
    if request.method == 'POST':
        selected_contacts = request.POST.getlist('selected_contacts')
        if selected_contacts:
            UserContactList.objects.filter(id__in=selected_contacts, user=request.user).delete()
            return redirect('contacts_list')
    return redirect('contacts_list')
# Adding contact list feature End here ---------------------------------------------------------------------------------------


# @login_required -------------------------------------------------------------- that was test
# def test_details(request):
#     user_subscription = UserSubscription.objects.filter(user=request.user).first()

#     context = {'subscription': user_subscription}

#     contacts_limit = user_subscription.plan.contacts  # Ensure this attribute exists
#     print(f"{contacts_limit}")
#     return render(request, 'test/test.html', context)
# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import UserContactList, UserSubscription, UserContactSearch

@login_required
def contact_search(request):
    if request.method == 'POST':
        city = request.POST.get('city')
        state = request.POST.get('state')
        country = request.POST.get('country')
        precinct_number = request.POST.get('precinct_number')  # Now correctly using 'precinct_number'
        district = request.POST.get('district')
        ward = request.POST.get('ward')
        zipcode = request.POST.get('zipcode')

        # Save or update the user's search in UserContactSearch model
        user_search, created = UserContactSearch.objects.get_or_create(user=request.user)
        user_search.city = city
        user_search.state = state
        user_search.country = country
        user_search.pct_nbr = precinct_number  # Updated to 'pct_nbr'
        user_search.district = district
        user_search.ward = ward
        user_search.zipcode = zipcode
        user_search.save()

        return redirect('contact_search_results')

    # Get the user's last search to prefill the form
    last_search = UserContactSearch.objects.filter(user=request.user).first()

    # Get all search entries for the user to display
    search_history = UserContactSearch.objects.filter(user=request.user).order_by('-search_date')
    username = request.user.username if request.user.is_authenticated else None

    context = {
        'last_search': last_search,
        'search_history': search_history,  # Pass search history to the template
        'username': username,
    }
    return render(request, 'contactlists/contact_search.html', context)

# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import UserContactList, UserSubscription, UserContactSearch
@login_required
def contact_search_results(request):
    user_subscription = get_object_or_404(UserSubscription, user=request.user)
    contacts_limit = user_subscription.plan.contacts  # Number of contacts allowed by user's subscription

    # Get the last search details
    user_search = UserContactSearch.objects.filter(user=request.user).first()

    # Prepare the base queryset for the user's contacts and limit it to the user's subscription plan
    queryset = UserContactList.objects.filter(user=request.user)[:contacts_limit]

    # Convert queryset to a list to filter in Python
    limited_contacts = list(queryset)

    # Now, filter the limited contacts based on user input
    results = limited_contacts

    if user_search:
        # Apply filtering based on user input
        if user_search.city:
            results = [contact for contact in results if user_search.city.lower() in contact.city.lower()]
        if user_search.state:
            results = [contact for contact in results if user_search.state.lower() in contact.state.lower()]
        if user_search.country:
            results = [contact for contact in results if user_search.country.lower() in contact.country.lower()]
        if user_search.zipcode:
            results = [contact for contact in results if user_search.zipcode.lower() in contact.zipcode.lower()]
        if user_search.district:
            results = [contact for contact in results if user_search.district.lower() in contact.district.lower()]
        if user_search.pct_nbr:  # Updated to use 'pct_nbr'
            results = [contact for contact in results if user_search.pct_nbr.lower() in contact.pct_nbr.lower()]
        if user_search.ward:
            results = [contact for contact in results if user_search.ward.lower() in contact.ward.lower()]

    # Limit the results further based on the subscription limit if necessary
    results = results[:contacts_limit]

    context = {
        'results': results,
        'search': user_search,
    }
    return render(request, 'contactlists/contact_search_results.html', context)


# Downloading data of contact  -----------------------------------------------------------------------
import csv
from django.http import HttpResponse

from django.http import HttpResponse
import csv
from .models import UserContactList, UserSubscription
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

@login_required
def download_contacts_csv(request):
    # Fetch the user's contacts from the database
    user_contacts = UserContactList.objects.filter(user=request.user)
    
    # Get the user's subscription plan to enforce the contact limit
    user_subscription = get_object_or_404(UserSubscription, user=request.user)
    contacts_limit = user_subscription.plan.contacts

    if contacts_limit is not None:
        user_contacts = user_contacts[:contacts_limit]  # Limit the contacts based on the subscription plan

    # Create the HttpResponse object with CSV headers
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="user_contacts.csv"'

    # Initialize the CSV writer
    writer = csv.writer(response)

    # Write the header row based on the format you provided
    writer.writerow([
        'STATE_ID', 'VOTER_NBR', 'LNAME', 'FNAME', 'TITLE', 'ADDRESS', 'ADDRESS2', 'CITY', 'STATE', 'ZIP',
        'PHONE', 'DOB', 'REG_DATE', 'DISTRICT', 'PCT_NBR', 'WARD', 'EMAIL'
    ])

    # Loop through each contact and write the respective data to the CSV file
    for contact in user_contacts:
        # Format the dates to MM/DD/YYYY
        dob = contact.dob.strftime('%m/%d/%Y') if contact.dob else ''
        reg_date = contact.reg_date.strftime('%m/%d/%Y') if contact.reg_date else ''

        writer.writerow([
            contact.state_id, contact.voter_nbr, contact.last_name, contact.first_name, contact.title,
            contact.address, contact.address2, contact.city, contact.state, contact.zipcode,
            contact.phone, dob, reg_date, contact.district, contact.pct_nbr,
            contact.ward, contact.email
        ])

    return response


import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Poltaker

@login_required
def download_poltakers_csv(request):
    # Get the poltakers associated with the authenticated user
    user_poltakers = Poltaker.objects.filter(user=request.user)

    # Create the HttpResponse object with CSV headers
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="poltakers_data.csv"'

    writer = csv.writer(response)
    # Header row for all fields in the Poltaker model
    writer.writerow([
        'Name', 'Mobile', 'Email', 'Zip Code', 'Street', 'City', 'State',
        'Completed Surveys', 'In-Progress Surveys', 'Pending Surveys',
        'Total Surveys', 'Password Changed'
    ])

    # Write each poltaker's data row
    for poltaker in user_poltakers:
        writer.writerow([
            poltaker.name, poltaker.mobile, poltaker.email, poltaker.zip_code,
            poltaker.Street, poltaker.city, poltaker.state, 
            poltaker.completed_surveys, poltaker.inprogress_surveys,
            poltaker.pending_surveys, poltaker.total_survey, 
            poltaker.password_changed
        ])

    return response





# ADding survey data for user 
# views.py of walkapp
import csv
from django.http import HttpResponse
from django.shortcuts import render
from surveyapp.models import Survey, SurveyResponse  # Import the models from surveyapp

# View to display surveys created by the logged-in user
# def my_surveys(request):
#     # Ensure the user is logged in and filter surveys based on user (created_by)
#     surveys = Survey.objects.filter(created_by=request.user)
    
#     context = {
#         'surveys': surveys,
#     }
#     return render(request, 'surveydata/my_surveys.html', context)
# import csv
# from django.http import HttpResponse
# from surveyapp.models import SurveyResponse, Survey  # Import from surveyapp
# from walkapp.models import Question, Option  # Import from walkapp
# from walkapp.models import Poltaker  # Import Poltaker model

# def export_responses_as_csv(request, survey_id):
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
#               'Polltaker Street', 'Polltaker City', 'Polltaker State', 'Contact Name', 'Contact Email']

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

# import csv
# from django.http import HttpResponse
# from surveyapp.models import SurveyResponse, Survey  # Import from surveyapp
# from walkapp.models import Question, Option  # Import from walkapp

# def export_responses_as_csv(request, survey_id):
#     # Get the survey object
#     survey = Survey.objects.get(id=survey_id)

#     # Fetch all responses for this survey
#     responses = SurveyResponse.objects.filter(survey=survey)

#     # Create the HttpResponse with CSV content type
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = f'attachment; filename="{survey.title}_responses.csv"'

#     # Create a CSV writer
#     writer = csv.writer(response)

#     # Prepare header row - it will contain question text in the first column and the response in the second column
#     header = ['Polltaker']  # Start with Polltaker as the first column
#     questions = list(survey.questions.all())  # List of questions for this survey
#     for question in questions:
#         header.append(question.question_text)  # Use the correct attribute name here (question_text)
    
#     writer.writerow(header)  # Write the header row to the CSV

#     # Loop through each survey response and write data to the CSV
#     for response_data in responses:
#         row = [response_data.polltaker.name]  # Start row with polltaker name (or other identifier)

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


# User details edit   start --------------------------------------------------------------------
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import UserProfile

from django.contrib import messages

@login_required
def edit_user_profile(request):
    user_profile = UserProfile.objects.filter(user=request.user).first()

    if request.method == 'POST':
        user_profile.first_name = request.POST.get('first_name')
        user_profile.last_name = request.POST.get('last_name')
        user_profile.phone_number = request.POST.get('phone_number')
        user_profile.country = request.POST.get('country')
        user_profile.city = request.POST.get('city')
        user_profile.street = request.POST.get('street')
        user_profile.zip_code = request.POST.get('zip_code')

        if 'profile_pic' in request.FILES:
            user_profile.profile_pic = request.FILES['profile_pic']

        user_profile.save()

        # Send a success message
        messages.success(request, 'Profile updated successfully!')

        # Redirect to the same page to show the message
        return redirect('edit_user_profile')
    username = request.user.username if request.user.is_authenticated else None

    context = {
        'profile': user_profile,
        'username':username,
    }
    return render(request, 'user/edit_user_profile.html', context)


@login_required
def verify_password(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        
        # Authenticate the user
        user = authenticate(request, username=request.user.username, password=password)
        
        if user is not None:
            # Password is correct, so redirect to the update email page
            return redirect('update_email')
        else:
            messages.error(request, "Incorrect password. Please try again.")
    
    return render(request, 'user/verify_password.html')


@login_required
def update_email(request):
    if request.method == 'POST':
        new_email = request.POST.get('new_email')

        # Check if the new email is the same as the current one or already in use
        if new_email == request.user.email:
            messages.error(request, "Please enter a different email.")
        elif User.objects.filter(email=new_email).exists():
            messages.error(request, "This email is already in use. Please choose a different email.")
        else:
            # Update the email
            request.user.email = new_email
            request.user.save()
            messages.success(request, "Your email has been updated successfully!")
            return redirect('edit_user_profile')  # Or any other redirect after success
    
    return render(request, 'user/update_email.html')
# User details edit  End  --------------------------------------------------------------------

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Question

@csrf_exempt
def delete_question(request, question_id):
    if request.method == 'DELETE':
        try:
            question = Question.objects.get(id=question_id)
            question.delete()
            return JsonResponse({'message': 'Question deleted successfully.'}, status=200)
        except Question.DoesNotExist:
            return JsonResponse({'message': 'Question not found.'}, status=404)
    return JsonResponse({'message': 'Invalid request method.'}, status=400)


# Deleting poltaker Start --------------------------------------------------------------------------------------------------------

@login_required
def poltaker_edit(request, pk):
    poltaker = get_object_or_404(Poltaker, pk=pk, user=request.user)
    if request.method == "POST":
        poltaker.name = request.POST.get('name')
        poltaker.mobile = request.POST.get('mobile')
        poltaker.email = request.POST.get('email')
        poltaker.zip_code = request.POST.get('zip_code')
        poltaker.Street = request.POST.get('Street')
        poltaker.city = request.POST.get('city')
        poltaker.state = request.POST.get('state')
        poltaker.completed_surveys = request.POST.get('completed_surveys')
        poltaker.inprogress_surveys = request.POST.get('inprogress_surveys')
        poltaker.pending_surveys = request.POST.get('pending_surveys')
        poltaker.total_survey = request.POST.get('total_survey')
        poltaker.save()
        return redirect('add_poltaker')
    return render(request, 'poltaker/poltaker_edit.html', {'poltaker': poltaker})

@login_required
def poltaker_delete(request, pk):
    poltaker = get_object_or_404(Poltaker, pk=pk, user=request.user)
    if request.method == "POST":
        poltaker.delete()
        return redirect('add_poltaker')
    return render(request, 'poltaker/poltaker_confirm_delete.html', {'poltaker': poltaker})
# Deleting poltaker End --------------------------------------------------------------------------------------------------------
from django.http import JsonResponse
from .models import Question
from django.views.decorators.csrf import csrf_exempt

# View to remove a single question
def remove_question(request, question_id):
    try:
        question = Question.objects.get(id=question_id)
        question.delete()
        return JsonResponse({'success': True, 'message': 'Question removed successfully.'})
    except Question.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Question not found.'})

# View to remove multiple selected questions
@csrf_exempt
def remove_selected_questions(request):
    if request.method == 'POST':
        try:
            # Parse the request body to get selected question IDs
            import json
            data = json.loads(request.body)
            question_ids = data.get('question_ids', [])

            # Remove the selected questions
            questions = Question.objects.filter(id__in=question_ids)
            questions.delete()

            return JsonResponse({'success': True, 'message': 'Selected questions removed successfully.'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

import csv
from django.http import HttpResponse
from .models import Question
@login_required
def export_questions(request):
    # Check if the user is authenticated
    if not request.user.is_authenticated:
        return HttpResponse("You are not authorized to export data.", status=403)

    # Fetch the questions for the logged-in user
    questions = Question.objects.filter(user=request.user).prefetch_related('options')

    # Create an HttpResponse object with CSV content type
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="questions.csv"'

    # Create a CSV writer object
    writer = csv.writer(response)

    # Write the header row (question text, question type, and options)
    writer.writerow(['question_text', 'question_type', 'option1', 'option2', 'option3', 'option4'])

    # Write questions and their options
    for question in questions:
        # Start with the question text and type
        row = [question.question_text, question.question_type]
        
        # For MCQ questions, add options
        if question.question_type == 'mcq':
            options = [option.option_text for option in question.options.all()]
            row.extend(options)  # Add options to the row

        # For text and yesno questions, leave option columns empty
        elif question.question_type == 'text' or question.question_type == 'yesno':
            row.extend([''] * 4)  # Empty options for text/yesno questions

        # Write the row to the CSV file
        writer.writerow(row)

    return response