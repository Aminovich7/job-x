from django.urls import path

from .views import (
    accept_bid_view,
    project_bids_view,
    project_detail_view,
    project_list_create_view,
)


urlpatterns = [
    path("", project_list_create_view),
    path("<int:project_id>/", project_detail_view),
    path("<int:project_id>/bids/", project_bids_view),
    path("<int:project_id>/bids/<int:bid_id>/accept/", accept_bid_view),
]
