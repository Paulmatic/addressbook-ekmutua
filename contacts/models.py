from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.search import SearchVectorField
from django.urls import reverse
from django.core.validators import EmailValidator, RegexValidator

User = get_user_model()

class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    shared_with = models.ManyToManyField(User, related_name='shared_files', blank=True)
    
    def __str__(self):
        return self.file.name

    class Meta:
        verbose_name = "Uploaded File"
        verbose_name_plural = "Uploaded Files"
        ordering = ['-uploaded_at']

class Contact(models.Model):
    FILE_STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('CLOSED', 'Closed'),
    ]
    
    CLIENT_STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('POTENTIAL', 'Potential'),
    ]

    first_name = models.CharField(
        max_length=50,
        verbose_name="First Name",
        help_text="Enter the contact's first name"
    )
    middle_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Middle Name",
        help_text="Enter the contact's middle name (optional)"
    )
    last_name = models.CharField(
        max_length=50,
        verbose_name="Last Name",
        help_text="Enter the contact's last name"
    )
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'."
        )],
        verbose_name="Phone Number",
        help_text="Format: +999999999"
    )
    email = models.EmailField(
        max_length=254,
        validators=[EmailValidator()],
        verbose_name="Email Address"
    )
    address = models.TextField(
        verbose_name="Full Address",
        help_text="Enter the complete mailing address"
    )
    file_status = models.CharField(
        max_length=6,
        choices=FILE_STATUS_CHOICES,
        default='OPEN',
        verbose_name="File Status"
    )
    file_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="File/Case Number",
        help_text="Unique identifier for this contact file"
    )
    client_status = models.CharField(
        max_length=9,
        choices=CLIENT_STATUS_CHOICES,
        default='ACTIVE',
        verbose_name="Client Status"
    )
    company = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Company/Organization"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Creation Date"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Last Updated"
    )
    search_vector = SearchVectorField(
        null=True,
        blank=True,
        verbose_name="Search Vector"
    )
    files = models.ManyToManyField(
        UploadedFile,
        blank=True,
        related_name='contacts',
        verbose_name="Associated Files"
    )

    class Meta:
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"
        indexes = [
            models.Index(fields=['file_number']),
            models.Index(fields=['first_name', 'last_name']),
            models.Index(fields=['search_vector'], name='contacts_contact_sv_idx'),
        ]
        ordering = ['last_name', 'first_name']
        constraints = [
            models.UniqueConstraint(
                fields=['first_name', 'last_name', 'email'],
                name='unique_contact'
            )
        ]

    def __str__(self):
        return f"{self.file_number}: {self.last_name}, {self.first_name}"

    def get_absolute_url(self):
        return reverse('contact-detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update search vector
        from django.contrib.postgres.search import SearchVector
        Contact.objects.filter(pk=self.pk).update(
            search_vector=SearchVector(
                'first_name',
                'last_name',
                'file_number',
                'email',
                'company',
                'address'
            )
        )

    @property
    def full_name(self):
        """Returns the contact's full name."""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"

    @property
    def formatted_phone(self):
        """Returns formatted phone number."""
        if len(self.phone_number) == 10:
            return f"({self.phone_number[:3]}) {self.phone_number[3:6]}-{self.phone_number[6:]}"
        return self.phone_number

    def get_associated_files(self, user=None):
        """Returns files associated with this contact, optionally filtered by user access"""
        if user:
            return self.files.filter(
                models.Q(uploaded_by=user) | 
                models.Q(shared_with=user)
            ).distinct()
        return self.files.all()