from django.urls import path

from .views import category_list_view, skill_list_view

urlpatterns = [
    path("skills/", skill_list_view),
    path("categories/", category_list_view),
]
