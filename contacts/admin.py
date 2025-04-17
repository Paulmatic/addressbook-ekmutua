from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from contacts.models import Contact, UploadedFile, ContactTag, ContactHistory

class FileInline(admin.TabularInline):
    model = Contact.files.through
    extra = 0
    verbose_name = _("Associated File")
    verbose_name_plural = _("Associated Files")
    fields = ('uploadedfile', 'get_file_type', 'get_uploaded_at', 'get_uploaded_by')
    readonly_fields = ('uploadedfile', 'get_file_type', 'get_uploaded_at', 'get_uploaded_by')
    
    def get_uploaded_at(self, obj):
        return obj.uploadedfile.uploaded_at
    get_uploaded_at.short_description = _("Uploaded At")
    
    def get_uploaded_by(self, obj):
        return obj.uploadedfile.uploaded_by
    get_uploaded_by.short_description = _("Uploaded By")
    
    def get_file_type(self, obj):
        return obj.uploadedfile.file.name.split('.')[-1].upper()
    get_file_type.short_description = _("Type")
    
    def has_add_permission(self, request, obj=None):
        return False

class HistoryInline(admin.TabularInline):
    model = ContactHistory
    extra = 0
    verbose_name = _("History Entry")
    verbose_name_plural = _("Change History")
    fields = ('changed_at', 'changed_by', 'change_description')
    readonly_fields = ('changed_at', 'changed_by', 'change_description')
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = (
        'file_number_link', 
        'full_name', 
        'company', 
        'status_badge', 
        'file_count',
        'created_at'
    )
    list_filter = (
        'client_status', 
        'file_status', 
        ('created_by', admin.RelatedOnlyFieldListFilter),
        ('tags', admin.RelatedOnlyFieldListFilter),
        'created_at'
    )
    search_fields = (
        'first_name', 
        'last_name', 
        'middle_name', 
        'file_number', 
        'email',
        'company',
        'address'
    )
    ordering = ('-created_at',)
    list_per_page = 25
    list_select_related = ('created_by',)
    autocomplete_fields = ('tags', 'assigned_to')
    filter_horizontal = ('files',)
    readonly_fields = (
        'created_at', 
        'updated_at', 
        'created_by',
        'search_vector_preview'
    )
    fieldsets = (
        (_("Basic Information"), {
            'fields': (
                ('first_name', 'middle_name', 'last_name'),
                ('file_number', 'created_at'),
            )
        }),
        (_("Contact Details"), {
            'fields': (
                ('email', 'phone_number'),
                'address',
                'company',
            )
        }),
        (_("Status Information"), {
            'fields': (
                ('client_status', 'file_status'),
                ('assigned_to', 'tags'),
            )
        }),
        (_("Files and Metadata"), {
            'fields': (
                'files',
                ('created_by', 'updated_at'),
                'search_vector_preview',
            ),
            'classes': ('collapse',)
        }),
    )
    inlines = [FileInline, HistoryInline]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(file_count=Count('files'))
        return qs
    
    def file_number_link(self, obj):
        url = reverse('admin:contacts_contact_change', args=[obj.id])
        return format_html('<a href="{}">{}</a>', url, obj.file_number)
    file_number_link.short_description = _("File Number")
    file_number_link.admin_order_field = 'file_number'
    
    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = _("Full Name")
    full_name.admin_order_field = ('last_name', 'first_name')
    
    def status_badge(self, obj):
        return format_html(
            '<span class="badge {}">{}</span>',
            'bg-success' if obj.client_status == 'ACTIVE' else 'bg-warning',
            obj.get_client_status_display()
        )
    status_badge.short_description = _("Status")
    
    def file_count(self, obj):
        return obj.file_count
    file_count.short_description = _("Files")
    file_count.admin_order_field = 'file_count'
    
    def search_vector_preview(self, obj):
        return format_html(
            '<div style="max-height: 100px; overflow: auto; font-family: monospace;">{}</div>',
            obj.search_vector
        )
    search_vector_preview.short_description = _("Search Vector Preview")
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ('file_number',)
        return self.readonly_fields

@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = (
        'file_name', 
        'category', 
        'uploaded_by', 
        'uploaded_at', 
        'shared_with_count',
        'is_public'
    )
    list_filter = (
        'category', 
        'is_public',
        ('uploaded_by', admin.RelatedOnlyFieldListFilter),
        'uploaded_at'
    )
    search_fields = (
        'file__name', 
        'description',
        'uploaded_by__username'
    )
    filter_horizontal = ('shared_with',)
    readonly_fields = (
        'uploaded_at', 
        'uploaded_by',
        'file_size_display'
    )
    
    def file_name(self, obj):
        return obj.file.name.split('/')[-1]
    file_name.short_description = _("File Name")
    
    def shared_with_count(self, obj):
        return obj.shared_with.count()
    shared_with_count.short_description = _("Shared With")
    
    def file_size_display(self, obj):
        size = obj.file.size
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size/1024:.1f} KB"
        else:
            return f"{size/(1024*1024):.1f} MB"
    file_size_display.short_description = _("File Size")
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(ContactTag)
class ContactTagAdmin(admin.ModelAdmin):
    list_display = (
        'colored_tag', 
        'created_by', 
        'contact_count',
        'created_at'
    )
    list_filter = (
        ('created_by', admin.RelatedOnlyFieldListFilter),
    )
    search_fields = ('name',)
    readonly_fields = ('created_by', 'created_at')
    
    def colored_tag(self, obj):
        return format_html(
            '<span class="badge" style="background-color: {}; color: {}">{}</span>',
            obj.color,
            'white' if obj.text_color == 'text-white' else 'black',
            obj.name
        )
    colored_tag.short_description = _("Tag")
    
    def contact_count(self, obj):
        return obj.contacts.count()
    contact_count.short_description = _("Contacts")
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(ContactHistory)
class ContactHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'contact_link',
        'changed_by',
        'changed_at',
        'change_summary'
    )
    list_filter = (
        'changed_at',
        ('changed_by', admin.RelatedOnlyFieldListFilter),
    )
    search_fields = (
        'contact__first_name',
        'contact__last_name',
        'contact__file_number',
        'change_description'
    )
    readonly_fields = (
        'contact',
        'changed_by',
        'changed_at',
        'change_description',
        'changed_fields_preview'
    )
    
    def contact_link(self, obj):
        url = reverse('admin:contacts_contact_change', args=[obj.contact.id])
        return format_html('<a href="{}">{}</a>', url, obj.contact)
    contact_link.short_description = _("Contact")
    
    def change_summary(self, obj):
        return obj.change_description[:50] + ('...' if len(obj.change_description) > 50 else '')
    change_summary.short_description = _("Change Summary")
    
    def changed_fields_preview(self, obj):
        return format_html(
            '<pre style="max-height: 300px; overflow: auto;">{}</pre>',
            obj.changed_fields
        )
    changed_fields_preview.short_description = _("Changed Fields (Detailed)")
    
    def has_add_permission(self, request):
        return False

class Media:
    css = {
        'all': (
            'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css',
            'admin/css/custom.css',
        )
    }
    js = (
        'admin/js/custom.js',
    )