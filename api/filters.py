import django_filters
from contacts.models import Contact

class ContactFilter(django_filters.FilterSet):
    file_number = django_filters.CharFilter(lookup_expr='icontains')
    last_name = django_filters.CharFilter(lookup_expr='icontains')
    client_status = django_filters.CharFilter(field_name='client_status')
    file_status = django_filters.CharFilter(field_name='file_status')

    class Meta:
        model = Contact
        fields = [
            'file_number', 'last_name', 
            'client_status', 'file_status'
        ]