from django.urls import path

from .views import (
    accept_bid_view,
    bid_withdraw_view,
    project_bids_view,
    project_cancel_view,
    project_detail_view,
    project_list_create_view,
    project_skills_view,
    project_update_view,
)


urlpatterns = [
    path("", project_list_create_view),
    path("<int:project_id>/", project_detail_view),
    path("<int:project_id>/cancel/", project_cancel_view),
    path("<int:project_id>/skills/", project_skills_view),
    path("<int:project_id>/bids/", project_bids_view),
    path("<int:project_id>/bids/<int:bid_id>/", bid_withdraw_view),
    path("<int:project_id>/bids/<int:bid_id>/accept/", accept_bid_view),
]
