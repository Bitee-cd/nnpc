from django.shortcuts import render,redirect
from django.core.files.storage import FileSystemStorage
from utils.helpers import get_headers,searchForDuplicates,searchFileStartingFromDate
import os
from django.http import FileResponse, Http404
from django.conf import settings

def index(request):
    if request.method == "POST":
        myfile = request.FILES.get('myfile')
        if myfile:
            fs = FileSystemStorage()
            file_path = os.path.join(settings.MEDIA_ROOT, myfile.name)
            if os.path.exists(file_path):  
                os.remove(file_path)
            filename = fs.save(myfile.name, myfile)
            file_path = fs.path(filename)
            headers = get_headers(file_path)
            print(os.path.join(settings.MEDIA_ROOT, filename),filename)
            request.session['step1_file'] = filename

            return render(request, 'step_one.html', {
                'headers': headers
            })
        elif 'selected_header' in request.POST:
            selected_header = request.POST.get('selected_header')
            start_date = request.POST.get('start_date')
          
            request.session['step1_header'] = selected_header
            request.session['start_date'] = start_date
            print("start_date: " ,start_date)
            return redirect('step_two') 
    return render(request, 'step_one.html')


def step_two(request):
    if request.method == "POST":
        myfile = request.FILES.get('myfile')
        if myfile:
            fs = FileSystemStorage()
            file_path = os.path.join(settings.MEDIA_ROOT, myfile.name)
            if os.path.exists(file_path):  
                os.remove(file_path)
            filename = fs.save(myfile.name, myfile)
            file_path = fs.path(filename)
            uploaded_file_url = fs.url(filename)
            headers = get_headers(file_path)
            print(os.path.join(settings.MEDIA_ROOT, filename))

            # Store file path and headers in session for step 2
            request.session['step2_file'] = filename
           

            return render(request, 'step_two.html', {
                'headers': headers
            })
        elif 'selected_header' in request.POST:
            selected_header = request.POST.get('selected_header')
            request.session['step2_header'] = selected_header
            return redirect('step_three') 
    return render(request, 'step_two.html')

def step_three(request):
    options = ["NNPC", "MOG","MON"]

    if request.method == "POST":
        selected_option = request.POST.get('option')

        # Store the selected option in session for step 3
        request.session['selected_option'] = selected_option

        # Now you have all the data in the session
        step1_file = request.session.get('step1_file')
        step1_header = request.session.get('step1_header')
        step2_file = request.session.get('step2_file')
        step2_header = request.session.get('step2_header')
        selected_option = request.session.get('selected_option')

        # Redirect or render the next step
        return  redirect('step_four')

    return render(request, 'step_three.html', {
        'options': options
    })

def step_four(request):
    if request.method== "GET":
        step1_file = request.session.get('step1_file')
        step1_header = request.session.get('step1_header')
        step2_file = request.session.get('step2_file')
        step2_header = request.session.get('step2_header')
        selected_option = request.session.get('selected_option')
        start_date = request.session.get('start_date')
        details = {
            "step1_file":step1_file,
            "step1_header":step1_header,
            "step2_file":step2_file,
            "step2_header":step2_header,
            "selected_option":selected_option,
            "start_date":start_date
            }
      
        return   render(request,'step_four.html',{"details":details})
    


def generate(request):
    
    step1_file = request.session.get('step1_file')
    step1_header = request.session.get('step1_header')
    step2_file = request.session.get('step2_file')
    step2_header = request.session.get('step2_header')
    selected_option = request.session.get('selected_option')
    start_date = request.session.get('start_date')
    
    step1_file_url =os.path.join(settings.MEDIA_ROOT, step1_file)
    step2_file_url =os.path.join(settings.MEDIA_ROOT, step2_file)
    details = {
                "step1_file":step1_file,
                "step1_header":step1_header,
                "step2_file":step2_file,
                "step2_header":step2_header,
                "selected_option":selected_option,
                "start_date":start_date
                }
    errors = []
    if not step1_file or not os.path.exists(step1_file_url):
        errors.append("Manifest file is missing.")
    if not step1_header:
        errors.append("Manifest header is missing.")
    if not step2_file or not os.path.exists(step2_file_url):
        errors.append("Company file is missing.")
    if not step2_header:
        errors.append("Company header is missing.")
    if not selected_option:
        errors.append("Selected company name is missing.")
    if not start_date:
        errors.append("Start date is missing.")

    if errors:
        return render(request, 'step_four.html', 
        { "errors": errors,"details":details})
    
   
   
    data = searchFileStartingFromDate(step1_file_url, step1_header, start_date, selected_option)

    duplicates_file_path, non_duplicates_file_path = searchForDuplicates(
        step2_file_url, step2_header, data, step1_file_url, step1_header
    )

    # return render(request, 'step_four.html', 
    #     { "details":details})
    return render(request, 'download.html', {
        'duplicates_file': os.path.basename(duplicates_file_path),
        'non_duplicates_file': os.path.basename(non_duplicates_file_path)
    })


def download_csv_file(file_path):
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
        return response
    else:
        raise Http404("File not found")
def download_duplicates(request):
    file_path = os.path.join(settings.MEDIA_ROOT, 'duplicates.csv')
    return download_csv_file(file_path)

def download_non_duplicates(request):
    file_path = os.path.join(settings.MEDIA_ROOT, 'non_duplicates.csv')
    return download_csv_file(file_path)




