from django.shortcuts import render
from django.http import JsonResponse


def index(request):
    context = {
        'company_name': 'Shiva Shakti Engineering and Construction',
    }
    return render(request, 'index.html', context)


def healthz(request):
    """Lightweight health check endpoint for readiness/liveness probes."""
    data = {'status': 'ok'}
    return JsonResponse(data)
