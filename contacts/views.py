from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import F
from contacts.models import Contact
from contacts.forms import ContactForm

class ContactListView(ListView):
    model = Contact
    template_name = 'contacts/contact_list.html'
    context_object_name = 'contacts'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(client_status=status)
        return queryset

class ContactCreateView(CreateView):
    model = Contact
    form_class = ContactForm
    template_name = 'contacts/contact_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Contact created successfully!')
        return response

    def get_success_url(self):
        return reverse_lazy('contact-detail', kwargs={'pk': self.object.pk})

class ContactUpdateView(UpdateView):
    model = Contact
    form_class = ContactForm
    template_name = 'contacts/contact_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Contact updated successfully!')
        return response

    def get_success_url(self):
        return reverse_lazy('contact-detail', kwargs={'pk': self.object.pk})

class ContactDetailView(DetailView):
    model = Contact
    template_name = 'contacts/contact_detail.html'

class ContactDeleteView(DeleteView):
    model = Contact
    template_name = 'contacts/contact_confirm_delete.html'
    success_url = reverse_lazy('contact-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Contact deleted successfully!')
        return super().delete(request, *args, **kwargs)

class ContactSearchView(ListView):
    model = Contact
    template_name = 'contacts/contact_search.html'
    paginate_by = 20

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            search_query = SearchQuery(query)
            return Contact.objects.annotate(
                rank=SearchRank(F('search_vector'), search_query)
            ).filter(search_vector=search_query).order_by('-rank')
        return Contact.objects.none()