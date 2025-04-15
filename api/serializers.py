from rest_framework import serializers
from contacts.models import Contact

class ContactSerializer(serializers.ModelSerializer):
    client_status_display = serializers.CharField(source='get_client_status_display', read_only=True)
    file_status_display = serializers.CharField(source='get_file_status_display', read_only=True)
    
    class Meta:
        model = Contact
        fields = [
            'id', 'first_name', 'middle_name', 'last_name',
            'phone_number', 'email', 'address', 'file_status',
            'file_status_display', 'file_number', 'client_status',
            'client_status_display', 'company', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'search_vector']