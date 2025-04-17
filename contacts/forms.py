from django import forms
from django.db import models
from django.contrib.auth import get_user_model
from .models import Contact, UploadedFile
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class ContactForm(forms.ModelForm):
    files = forms.ModelMultipleChoiceField(
        queryset=UploadedFile.objects.none(),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        required=False,
        label=_("Associated Files")
    )
    new_files = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'multiple': True
        }),
        label=_("Upload New Files")
    )

    class Meta:
        model = Contact
        fields = [
            'first_name', 'middle_name', 'last_name',
            'phone_number', 'email', 'address',
            'file_status', 'file_number', 'client_status',
            'company', 'files', 'tags'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter first name')
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter middle name')
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter last name')
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('+1234567890')
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _('email@example.com')
            }),
            'address': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': _('Enter complete address')
            }),
            'file_status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'file_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Auto-generated if empty')
            }),
            'client_status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Company name')
            }),
            'tags': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'data-placeholder': _('Select tags...')
            }),
        }
        labels = {
            'file_number': _('File/Case Number'),
            'file_status': _('File Status'),
            'client_status': _('Client Status'),
        }
        help_texts = {
            'file_number': _('Leave blank to auto-generate'),
            'phone_number': _('Format: +[country code][number]'),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Set queryset for files field based on user permissions
            self.fields['files'].queryset = UploadedFile.objects.filter(
                models.Q(uploaded_by=user) | 
                models.Q(shared_with=user) |
                models.Q(is_public=True)
            ).distinct()
            
            # Set initial files for existing contacts
            if self.instance and self.instance.pk:
                self.fields['files'].initial = self.instance.files.all()
                
            # Limit tag choices to those created by the user
            self.fields['tags'].queryset = self.fields['tags'].queryset.filter(
                created_by=user
            )

    def clean_file_number(self):
        file_number = self.cleaned_data.get('file_number')
        if not file_number and not self.instance.pk:
            # Auto-generate file number if not provided for new contacts
            last_contact = Contact.objects.order_by('-id').first()
            last_id = last_contact.id if last_contact else 0
            return f"CL-{last_id + 1:05d}"
        return file_number

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if commit:
            instance.save()
            
        # Save many-to-many relationships
        self.save_m2m()
        
        # Handle new file uploads
        new_files = self.files.uploaded_files if hasattr(self.files, 'uploaded_files') else []
        for uploaded_file in new_files:
            new_file = UploadedFile(
                file=uploaded_file,
                uploaded_by=self.user
            )
            new_file.save()
            instance.files.add(new_file)
            
        return instance


class FileUploadForm(forms.ModelForm):
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 2,
            'class': 'form-control',
            'placeholder': _('File description (optional)')
        })
    )
    is_public = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label=_('Make this file public'),
        help_text=_('Public files can be viewed by all users')
    )

    class Meta:
        model = UploadedFile
        fields = ['file', 'category', 'description', 'shared_with', 'is_public']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'shared_with': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'data-placeholder': _('Select users to share with...')
            })
        }
        labels = {
            'file': _('Select File'),
            'category': _('File Category'),
            'shared_with': _('Share With Users')
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            # Exclude current user from shared_with choices
            self.fields['shared_with'].queryset = User.objects.exclude(id=self.user.id)
            # Set initial category
            self.fields['category'].initial = 'DOC'

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Validate file size (10MB limit)
            max_size = 10 * 1024 * 1024
            if file.size > max_size:
                raise forms.ValidationError(
                    _('File too large. Maximum size is 10MB.')
                )
            
            # Validate file extensions
            valid_extensions = [
                '.pdf', '.doc', '.docx', 
                '.jpg', '.jpeg', '.png',
                '.xls', '.xlsx', '.txt'
            ]
            if not any(file.name.lower().endswith(ext) for ext in valid_extensions):
                raise forms.ValidationError(
                    _('Unsupported file type. Allowed types: ') +
                    ', '.join(ext.strip('.') for ext in valid_extensions)
                )
                
        return file


class ContactFilterForm(forms.Form):
    STATUS_CHOICES = [
        ('', _('All Statuses')),
        *Contact.FileStatus.choices
    ]
    
    CLIENT_CHOICES = [
        ('', _('All Clients')),
        *Contact.ClientStatus.choices
    ]

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Search by name, email, or file number...')
        })
    )
    file_status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    client_status = forms.ChoiceField(
        choices=CLIENT_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=Contact.tags.field.related_model.objects.none(),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select',
            'data-placeholder': _('Filter by tags...')
        })
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['tags'].queryset = Contact.tags.field.related_model.objects.filter(
                created_by=user
            )