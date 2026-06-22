from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from contracts.models import Review
from skills.serializers import SkillSerializer
from users.models import User

from .filters import FreelancerFilter
from .serializers import FreelancerReviewSerializer, FreelancerSerializer


class FreelancerPagination(PageNumberPagination):
    page_size = 10


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@extend_schema(responses=FreelancerSerializer(many=True))
def freelancer_list_view(request):
    freelancers = User.objects.filter(role=User.ROLE_FREELANCER)
    filterset = FreelancerFilter(request.query_params, queryset=freelancers)
    filterset.is_valid()
    if filterset.errors:
        raise ValidationError(filterset.errors)
    paginator = FreelancerPagination()
    page = paginator.paginate_queryset(filterset.qs, request)
    serializer = FreelancerSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@extend_schema(responses=FreelancerReviewSerializer(many=True))
def freelancer_reviews_view(request, freelancer_id):
    freelancer = get_object_or_404(User, id=freelancer_id, role=User.ROLE_FREELANCER)
    reviews = Review.objects.filter(contract__freelancer=freelancer).select_related("contract__client")
    paginator = FreelancerPagination()
    page = paginator.paginate_queryset(reviews, request)
    serializer = FreelancerReviewSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@extend_schema(responses=SkillSerializer(many=True))
def freelancer_skills_view(request, freelancer_id):
    freelancer = get_object_or_404(User, id=freelancer_id, role=User.ROLE_FREELANCER)
    serializer = SkillSerializer(freelancer.skills.all(), many=True)
    return Response(serializer.data)
