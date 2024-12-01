# app/views.py
from django.http import JsonResponse
from .models import Message

def contact_view(request):
    if request.method == 'POST':
        # Get form data from POST request
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Save the form data to the database
        new_message = Message(full_name=full_name, email=email, message=message)
        new_message.save()

        # Return a success response
        return JsonResponse({'status': 'success', 'message': 'Your message has been submitted successfully!'})
    
    # If the request method is not POST, you can return an error response (optional)
    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})
