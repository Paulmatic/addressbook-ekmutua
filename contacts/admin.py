from django.contrib import admin
from contacts.models import Contact

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('file_number', 'last_name', 'first_name', 'email', 'client_status')
    list_filter = ('client_status', 'file_status')
    search_fields = ('first_name', 'last_name', 'file_number', 'email')
    ordering = ('last_name', 'first_name')