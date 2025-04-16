from django.urls import path
from contacts import views

app_name = 'contacts'

urlpatterns = [
    # Contact URLs
    path('', views.ContactListView.as_view(), name='contact-list'),
    path('new/', views.ContactCreateView.as_view(), name='contact-create'),
    path('<int:pk>/', views.ContactDetailView.as_view(), name='contact-detail'),
    path('<int:pk>/edit/', views.ContactUpdateView.as_view(), name='contact-update'),
    path('<int:pk>/delete/', views.ContactDeleteView.as_view(), name='contact-delete'),
    path('search/', views.ContactSearchView.as_view(), name='contact-search'),
    
    # File URLs
    path('files/upload/', views.upload_file, name='upload-file'),
    path('files/', views.file_list, name='file-list'),
]