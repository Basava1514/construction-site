from django.shortcuts import render

def index(request):
    context = {
        'company_name': 'Shiva Shakti Engineering and Construction',
    }
    return render(request, 'index.html', context)
