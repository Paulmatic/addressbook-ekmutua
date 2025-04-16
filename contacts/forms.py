from django import forms
from django.db import models
from .models import Contact, UploadedFile
from django.contrib.auth import get_user_model

User = get_user_model()

class ContactForm(forms.ModelForm):
    files = forms.ModelMultipleChoiceField(
        queryset=UploadedFile.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Associated Files"
    )

    class Meta:
        model = Contact
        fields = [
            'first_name', 'middle_name', 'last_name',
            'phone_number', 'email', 'address',
            'file_status', 'file_number', 'client_status',
            'company', 'files'
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

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Set queryset for files field based on user permissions
            self.fields['files'].queryset = UploadedFile.objects.filter(
                models.Q(uploaded_by=user) | 
                models.Q(shared_with=user)
            ).distinct()
            
            # Set initial files for existing contacts
            if self.instance and self.instance.pk:
                self.fields['files'].initial = self.instance.files.all()

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ['file', 'shared_with']
        widgets = {
            'shared_with': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'shared_with': 'Share With Users',
            'file': 'Select File'
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            # Exclude current user from shared_with choices
            self.fields['shared_with'].queryset = User.objects.exclude(id=self.user.id)