import django_filters
from django import forms
from django.contrib.auth.models import User
from .models import Labels, Status, Tasks


class TasksFilter(django_filters.FilterSet):
    status = django_filters.ModelChoiceFilter(
        queryset=Status.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    executor = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    label = django_filters.ModelChoiceFilter(
        queryset=Labels.objects.all(),
        field_name='labels',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    self_tasks = django_filters.BooleanFilter(
        method='filter_self_tasks',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Tasks
        fields = ['status', 'executor', 'label']

    def filter_self_tasks(self, queryset, name, value):

        if value and self.request and self.request.user.is_authenticated:
            return queryset.filter(executor=self.request.user)
        return queryset