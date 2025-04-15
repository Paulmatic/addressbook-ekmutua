from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from contacts.models import Contact
from api.serializers import ContactSerializer
from api.filters import ContactFilter

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ContactFilter
    search_fields = [
        'first_name', 'last_name', 'file_number',
        'email', 'company', 'address'
    ]
    ordering_fields = [
        'last_name', 'first_name', 'file_number',
        'client_status', 'created_at'
    ]
    ordering = ['last_name', 'first_name']