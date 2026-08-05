from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import ContactForm
import urllib.parse

WHATSAPP_BASE = 'https://wa.me/919845849799?text='


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            phone = form.cleaned_data['phone']
            service = form.cleaned_data.get('service', '')
            message = form.cleaned_data.get('message', '')
            text = f"Hello Guru H M,%0AI visited Shiva Shakti Engineering and Construction website.%0A%0AName:{name}%0APhone:{phone}%0AService:{service}%0AMessage:{message}%0A"
            url = WHATSAPP_BASE + urllib.parse.quote(text, safe='')
            return redirect(url)
    else:
        form = ContactForm()
    return render(request, 'contact/contact.html', {'form': form})
