from django import forms
from contacts.models import Contact

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = [
            'first_name', 'middle_name', 'last_name',
            'phone_number', 'email', 'address',
            'file_status', 'file_number', 'client_status',
            'company'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'file_status': forms.Select(attrs={'class': 'form-select'}),
            'client_status': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'file_number': 'File/Case Number',
            'file_status': 'File Status',
            'client_status': 'Client Status',
        }