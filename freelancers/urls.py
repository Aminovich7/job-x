from django.urls import path

from .views import freelancer_list_view, freelancer_reviews_view, freelancer_skills_view

urlpatterns = [
    path("", freelancer_list_view),
    path("<int:freelancer_id>/reviews/", freelancer_reviews_view),
    path("<int:freelancer_id>/skills/", freelancer_skills_view),
]
