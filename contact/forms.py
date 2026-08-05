from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(max_length=200, required=True)
    phone = forms.CharField(max_length=20, required=True)
    email = forms.EmailField(required=True)
    service = forms.CharField(max_length=200, required=False)
    message = forms.CharField(widget=forms.Textarea, required=False)

    def clean_phone(self):
        data = self.cleaned_data['phone']
        # Basic validation
        digits = ''.join(ch for ch in data if ch.isdigit())
        if len(digits) < 7:
            raise forms.ValidationError('Enter a valid phone number')
        return data
