import django_filters

from .models import Project


class ProjectFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(field_name="title", lookup_expr="icontains")
    min_budget = django_filters.NumberFilter(field_name="budget", lookup_expr="gte")
    max_budget = django_filters.NumberFilter(field_name="budget", lookup_expr="lte")

    class Meta:
        model = Project
        fields = ["search", "min_budget", "max_budget"]
