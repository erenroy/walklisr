from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from .forms import CSVUploadForm
from walkapp.models import Question, Option, User
import csv

def upload_csv(request):
    if request.method == "POST":
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']
            
            if not csv_file.name.endswith('.csv'):
                messages.error(request, "Please upload a valid CSV file.")
                return redirect("upload_csv")
            
            # Save the uploaded file
            fs = FileSystemStorage()
            filename = fs.save(csv_file.name, csv_file)
            file_path = fs.path(filename)

            # Try reading the CSV file with different encodings
            encodings = ['utf-8-sig', 'utf-8', 'ISO-8859-1', 'latin1']
            file_content = None
            for encoding in encodings:
                try:
                    with open(file_path, newline='', encoding=encoding) as csvfile:
                        file_content = csvfile.read()  # Try to read the content to detect the proper encoding
                        break
                except UnicodeDecodeError:
                    continue  # If decoding fails, try the next encoding

            if file_content is None:
                messages.error(request, "Failed to decode the CSV file. Please check the file encoding.")
                return redirect("upload_csv")

            # Parse the CSV file using the correct encoding
            with open(file_path, newline='', encoding=encoding) as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # Skip the header row
                
                # Loop through the CSV rows and add questions
                for row in reader:
                    if len(row) < 3:  # Skip rows with insufficient columns
                        continue
                    
                    question_text, question_type, *option_texts = row
                    if not question_text or not question_type:
                        continue  # Skip incomplete rows
                    
                    # Create the question for all users
                    users = User.objects.all()  # All users in the system
                    
                    for user in users:
                        question = Question.objects.create(
                            user=user,  # Set the user to each user
                            question_text=question_text,
                            question_type=question_type,
                        )

                        # Add options if it's a multiple choice question
                        if question_type == 'mcq' and option_texts:
                            for option_text in option_texts:
                                if option_text:
                                    Option.objects.create(question=question, option_text=option_text)

            messages.success(request, 'Questions uploaded successfully for all users.')
            return redirect("admin:walkapp_question_changelist")
    else:
        form = CSVUploadForm()

    return render(request, "admincustom/upload_csv.html", {"form": form})