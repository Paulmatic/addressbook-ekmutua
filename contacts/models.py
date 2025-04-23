from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.urls import reverse
from django.core.validators import EmailValidator, RegexValidator
from django.utils.translation import gettext_lazy as _

User = get_user_model()

# Choice definitions for new fields
JUDGEMENT_CHOICES = [
    ('allowed', 'Allowed'),
    ('dismissed', 'Dismissed'),
    ('referred', 'Referred'),
]

RULING_CHOICES = [
    ('allowed', 'Allowed'),
    ('dismissed', 'Dismissed'),
    ('referred', 'Referred'),
]

ORDER_CHOICES = [
    ('allowed', 'Allowed'),
    ('dismissed', 'Dismissed'),
    ('referred', 'Referred'),
]

PAYMENT_MODE_CHOICES = [
    ('cash', 'Cash'),
    ('mpesa', 'MPESA'),
    ('bank_transfer', 'Bank Transfer'),
    ('cheque', 'Cheque'),
]

class UploadedFile(models.Model):
    class FileCategory(models.TextChoices):
        DOCUMENT = 'DOC', _('Document')
        IMAGE = 'IMG', _('Image')
        AUDIO = 'AUD', _('Audio')
        VIDEO = 'VID', _('Video')
        OTHER = 'OTH', _('Other')

    file = models.FileField(
        upload_to='uploads/%Y/%m/%d/',
        verbose_name=_('File')
    )
    category = models.CharField(
        max_length=3,
        choices=FileCategory.choices,
        default=FileCategory.DOCUMENT,
        verbose_name=_('Category')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Description')
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Upload Date')
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='uploaded_files',
        verbose_name=_('Uploaded By')
    )
    shared_with = models.ManyToManyField(
        User,
        related_name='shared_files',
        blank=True,
        verbose_name=_('Shared With')
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name=_('Public Access')
    )

    def __str__(self):
        return f"{self.get_category_display()}: {self.file.name}"

    @property
    def file_type(self):
        return self.file.name.split('.')[-1].upper()

    @property
    def file_size(self):
        try:
            return f"{self.file.size / (1024 * 1024):.2f} MB"
        except (ValueError, OSError):
            return "N/A"

    class Meta:
        verbose_name = _("Uploaded File")
        verbose_name_plural = _("Uploaded Files")
        ordering = ['-uploaded_at']
        permissions = [
            ('share_file', 'Can share files with other users'),
            ('download_file', 'Can download files'),
        ]


class Contact(models.Model):
    class FileStatus(models.TextChoices):
        OPEN = 'OPEN', _('Open')
        CLOSED = 'CLOSED', _('Closed')
        PENDING = 'PEND', _('Pending')
        ARCHIVED = 'ARCH', _('Archived')

    class ClientStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', _('Active')
        INACTIVE = 'INACT', _('Inactive')
        POTENTIAL = 'POTEN', _('Potential')
        FORMER = 'FORMER', _('Former Client')

    first_name = models.CharField(
        max_length=50,
        verbose_name=_("First Name"),
        help_text=_("Enter the contact's first name")
    )
    middle_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("Middle Name"),
        help_text=_("Enter the contact's middle name (optional)")
    )
    last_name = models.CharField(
        max_length=50,
        verbose_name=_("Last Name"),
        help_text=_("Enter the contact's last name")
    )
    phone_number = models.CharField(
        max_length=20,
        validators=[RegexValidator(
            regex=r'^\+?[\d\s\-\(\)]{7,20}$',
            message=_("Phone number must be valid and between 7-20 digits.")
        )],
        verbose_name=_("Phone Number")
    )
    email = models.EmailField(
        max_length=254,
        validators=[EmailValidator()],
        verbose_name=_("Email Address"),
        unique=True
    )
    alternate_email = models.EmailField(
        max_length=254,
        blank=True,
        null=True,
        verbose_name=_("Alternate Email")
    )
    address = models.TextField(
        verbose_name=_("Full Address"),
        help_text=_("Enter the complete mailing address")
    )
    file_status = models.CharField(
        max_length=6,
        choices=FileStatus.choices,
        default=FileStatus.OPEN,
        verbose_name=_("File Status")
    )
    file_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("File/Case Number"),
        help_text=_("Unique identifier for this contact file")
    )
    file_open_date = models.DateField(
        verbose_name=_("File Open Date"),
        help_text=_("Date when the file/case was opened"),
        blank=True,
        null=True
    )
    client_status = models.CharField(
        max_length=9,
        choices=ClientStatus.choices,
        default=ClientStatus.ACTIVE,
        verbose_name=_("Client Status")
    )
    company = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Company/Organization")
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Internal Notes")
    )
    
    # New judgement fields
    judgement = models.CharField(
        max_length=20,
        choices=JUDGEMENT_CHOICES,
        blank=True,
        null=True,
        verbose_name=_("Judgement")
    )
    judgement_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Judgement Date")
    )
    
    # New ruling fields
    ruling = models.CharField(
        max_length=20,
        choices=RULING_CHOICES,
        blank=True,
        null=True,
        verbose_name=_("Ruling")
    )
    ruling_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Ruling Date")
    )
    
    # New order fields
    order = models.CharField(
        max_length=20,
        choices=ORDER_CHOICES,
        blank=True,
        null=True,
        verbose_name=_("Order")
    )
    order_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Order Date")
    )
    
    # New payment fields
    payment_mode = models.CharField(
        max_length=20,
        choices=PAYMENT_MODE_CHOICES,
        blank=True,
        null=True,
        verbose_name=_("Payment Mode")
    )
    payment_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Payment Date")
    )
    receipt_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("Receipt Number")
    )
    receipt_attachment = models.FileField(
        upload_to='receipts/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name=_("Receipt Attachment")
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Creation Date")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Last Updated")
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_contacts',
        verbose_name=_("Created By")
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_contacts',
        verbose_name=_("Assigned To")
    )
    search_vector = SearchVectorField(
        null=True,
        blank=True,
        verbose_name=_("Search Vector")
    )
    files = models.ManyToManyField(
        UploadedFile,
        blank=True,
        related_name='contacts',
        verbose_name=_("Associated Files")
    )
    tags = models.ManyToManyField(
        'ContactTag',
        blank=True,
        related_name='contacts',
        verbose_name=_("Tags")
    )

    class Meta:
        verbose_name = _("Contact")
        verbose_name_plural = _("Contacts")
        indexes = [
            models.Index(fields=['file_number']),
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['email']),
            models.Index(fields=['company']),
            models.Index(fields=['search_vector'], name='contact_search_idx'),
        ]
        ordering = ['last_name', 'first_name']
        constraints = [
            models.UniqueConstraint(
                fields=['first_name', 'last_name', 'email'],
                name='unique_contact'
            )
        ]
        permissions = [
            ('export_contact', 'Can export contact data'),
            ('merge_contact', 'Can merge duplicate contacts'),
        ]

    def __str__(self):
        return f"{self.file_number}: {self.last_name}, {self.first_name}"

    def get_absolute_url(self):
        return reverse('contact-detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        # Auto-generate file number if not provided
        if not self.file_number:
            last_contact = Contact.objects.order_by('-id').first()
            last_id = last_contact.id if last_contact else 0
            self.file_number = f"CL-{last_id + 1:05d}"
        
        # Set file open date if not provided and this is a new record
        if not self.pk and not self.file_open_date:
            self.file_open_date = timezone.now().date()
        
        super().save(*args, **kwargs)
        
        # Update search vector
        Contact.objects.filter(pk=self.pk).update(
            search_vector=SearchVector(
                'first_name',
                'last_name',
                'file_number',
                'email',
                'alternate_email',
                'company',
                'address',
                'notes',
                config='english'
            )
        )

    @property
    def full_name(self):
        """Returns the contact's full name."""
        names = [self.first_name]
        if self.middle_name:
            names.append(self.middle_name)
        names.append(self.last_name)
        return ' '.join(names)

    @property
    def formatted_phone(self):
        """Returns formatted phone number."""
        digits = ''.join(filter(str.isdigit, self.phone_number))
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        return self.phone_number

    def get_associated_files(self, user=None):
        """Returns files associated with this contact, optionally filtered by user access"""
        queryset = self.files.all()
        if user:
            queryset = queryset.filter(
                models.Q(uploaded_by=user) | 
                models.Q(shared_with=user) |
                models.Q(is_public=True)
            ).distinct()
        return queryset

    def get_status_badge(self):
        """Returns Bootstrap badge HTML for status"""
        status_map = {
            'OPEN': 'bg-primary',
            'CLOSED': 'bg-secondary',
            'PEND': 'bg-warning text-dark',
            'ARCH': 'bg-dark',
            'ACTIVE': 'bg-success',
            'INACT': 'bg-danger',
            'POTEN': 'bg-info',
            'FORMER': 'bg-light text-dark'
        }
        status = self.file_status if hasattr(self, 'file_status') else self.client_status
        return f'<span class="badge {status_map.get(status, "bg-light text-dark")}">{self.get_file_status_display()}</span>'


class ContactTag(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Tag Name")
    )
    color = models.CharField(
        max_length=7,
        default='#6c757d',
        verbose_name=_("Tag Color"),
        help_text=_("Hex color code (e.g. #6c757d)")
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_tags',
        verbose_name=_("Created By")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At")
    )

    class Meta:
        verbose_name = _("Contact Tag")
        verbose_name_plural = _("Contact Tags")
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def text_color(self):
        """Returns appropriate text color based on background color"""
        hex_color = self.color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        luminance = (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255
        return 'text-white' if luminance < 0.5 else 'text-dark'


class ContactHistory(models.Model):
    contact = models.ForeignKey(
        Contact,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name=_("Contact")
    )
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("Changed By")
    )
    changed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Changed At")
    )
    change_description = models.TextField(
        verbose_name=_("Change Description")
    )
    changed_fields = models.JSONField(
        verbose_name=_("Changed Fields")
    )

    class Meta:
        verbose_name = _("Contact History")
        verbose_name_plural = _("Contact Histories")
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.contact} - {self.changed_at}"