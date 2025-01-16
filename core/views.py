from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy

from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .models import Settings
from .forms import SettingsForm
from .mixins import RedirectMixin
from Core.functions import get_all_related_objects
from django.contrib import messages

# Create your views here.
class SettingsCreateView(RedirectMixin, CreateView):
    model = Settings
    form_class = SettingsForm
    template_name = 'Core/settings.html'
    success_url = reverse_lazy('daily-transactions')

class SettingsUpdateView(RedirectMixin, UpdateView):
    model = Settings
    form_class = SettingsForm
    template_name = 'Core/settings.html'
    success_url = reverse_lazy('daily-transactions')

class RestrictedDeleteView(RedirectMixin, DeleteView):
    template_name = 'delete.html'
    message = 'এটি উপরোক্ত হিসাবে ব্যবহৃত হয়েছে তাই ডিলিট করা যাবেনা।'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Determine related objects based on type
        related_objects = get_all_related_objects(self.object)

        # Delete if no related objects exist, otherwise render the list
        if len(related_objects) == 0:
            self.object.delete()
            return HttpResponseRedirect(self.get_success_url())
        else:
            messages.error(request, self.message)
            return render(request, self.template_name, {
                'object': self.object,
                'related_objects': related_objects,
                'previous_url': request.META.get('HTTP_REFERER'),
            })