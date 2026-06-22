import django_filters
from django.db.models import Q

from users.models import User


class FreelancerFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = User
        fields = ["search"]

    def filter_search(self, queryset, name, value):
        return queryset.filter(Q(username__icontains=value) | Q(bio__icontains=value))
