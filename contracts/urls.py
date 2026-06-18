from django.urls import path

from .views import contract_detail_view, contract_list_view, finish_contract_view, review_contract_view


urlpatterns = [
    path("", contract_list_view),
    path("<int:contract_id>/", contract_detail_view),
    path("<int:contract_id>/finish/", finish_contract_view),
    path("<int:contract_id>/review/", review_contract_view),
]
