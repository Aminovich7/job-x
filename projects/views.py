from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema

from contracts.models import Contract
from skills.models import Skill
from skills.serializers import SkillSerializer
from .filters import ProjectFilter
from .models import Bid, Project
from .permissions import (
    IsAuthenticatedClientWrite,
    IsAuthenticatedFreelancerBidWrite,
    IsClient,
    IsFreelancer,
    IsProjectOwner,
    enforce_permission,
)
from .serializers import (
    AcceptBidSerializer,
    BidSerializer,
    ProjectSerializer,
    ProjectUpdateSerializer,
)


class ProjectPagination(PageNumberPagination):
    page_size = 10


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticatedClientWrite])
@extend_schema(
    methods=["GET"],
    parameters=[
        OpenApiParameter("search", OpenApiTypes.STR, OpenApiParameter.QUERY, required=False),
        OpenApiParameter("min_budget", OpenApiTypes.STR, OpenApiParameter.QUERY, required=False),
        OpenApiParameter("max_budget", OpenApiTypes.STR, OpenApiParameter.QUERY, required=False),
    ],
    responses=ProjectSerializer(many=True),
)
@extend_schema(methods=["POST"], request=ProjectSerializer, responses=ProjectSerializer)
def project_list_create_view(request):
    if request.method == "GET":
        projects = Project.objects.filter(status=Project.STATUS_OPEN)
        filterset = ProjectFilter(request.query_params, queryset=projects)
        filterset.is_valid()
        if filterset.errors:
            raise ValidationError(filterset.errors)
        projects = filterset.qs

        paginator = ProjectPagination()
        page = paginator.paginate_queryset(projects, request)
        serializer = ProjectSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    enforce_permission(request, IsClient)

    serializer = ProjectSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    project = serializer.save(client=request.user)
    return Response(ProjectSerializer(project).data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@extend_schema(responses=ProjectSerializer)
def project_detail_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    return Response(ProjectSerializer(project).data)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticatedFreelancerBidWrite])
@extend_schema(methods=["GET"], responses=BidSerializer(many=True))
@extend_schema(methods=["POST"], request=BidSerializer, responses=BidSerializer)
def project_bids_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == "GET":
        enforce_permission(request, IsProjectOwner, project)
        serializer = BidSerializer(project.bids.all(), many=True)
        return Response(serializer.data)

    enforce_permission(request, IsFreelancer)

    serializer = BidSerializer(
        data=request.data,
        context={
            "request": request,
            "project": project,
            "freelancer": request.user,
        },
    )
    serializer.is_valid(raise_exception=True)
    bid = serializer.save(project=project, freelancer=request.user)
    return Response(BidSerializer(bid).data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@extend_schema(request=None, responses=AcceptBidSerializer)
def accept_bid_view(request, project_id, bid_id):
    project = get_object_or_404(Project, id=project_id)
    enforce_permission(request, IsProjectOwner, project)
    if project.status != Project.STATUS_OPEN:
        raise ValidationError({"project": "Project must be open to accept a bid."})

    bid = get_object_or_404(project.bids, id=bid_id)

    with transaction.atomic():
        bid.status = Bid.STATUS_ACCEPTED
        bid.save(update_fields=["status"])
        project.bids.exclude(id=bid.id).update(status=Bid.STATUS_REJECTED)
        project.status = Project.STATUS_IN_PROGRESS
        project.save(update_fields=["status"])
        contract = Contract.objects.create(
            project=project,
            client=project.client,
            freelancer=bid.freelancer,
            agreed_price=bid.price,
        )

    payload = {
        "bid_id": bid.id,
        "status": bid.status,
        "project_status": project.status,
        "contract_id": contract.id,
    }
    return Response(AcceptBidSerializer(payload).data, status=status.HTTP_200_OK)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
@extend_schema(request=ProjectUpdateSerializer, responses=ProjectSerializer)
def project_update_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    enforce_permission(request, IsProjectOwner, project)
    serializer = ProjectUpdateSerializer(project, data=request.data, partial=True, context={"project": project})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(ProjectSerializer(project).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@extend_schema(responses=ProjectSerializer)
def project_cancel_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    enforce_permission(request, IsProjectOwner, project)
    if project.status != Project.STATUS_OPEN:
        raise ValidationError({"project": "Only open projects can be cancelled."})
    project.status = Project.STATUS_CANCELLED
    project.save(update_fields=["status"])
    return Response(ProjectSerializer(project).data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
@extend_schema(responses=None)
def bid_withdraw_view(request, project_id, bid_id):
    enforce_permission(request, IsFreelancer)
    project = get_object_or_404(Project, id=project_id)
    bid = get_object_or_404(Bid, id=bid_id, project=project)
    if bid.freelancer != request.user:
        raise PermissionDenied("You can only withdraw your own bids.")
    if bid.status != Bid.STATUS_PENDING:
        raise ValidationError({"bid": "Only pending bids can be withdrawn."})
    bid.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "POST", "DELETE"])
@permission_classes([IsAuthenticated])
@extend_schema(responses=SkillSerializer(many=True))
def project_skills_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    enforce_permission(request, IsProjectOwner, project)

    if request.method == "GET":
        return Response(SkillSerializer(project.skills.all(), many=True).data)

    skill_id = request.data.get("skill_id")
    if not skill_id:
        return Response({"skill_id": "This field is required."}, status=status.HTTP_400_BAD_REQUEST)
    skill = get_object_or_404(Skill, id=skill_id)

    if request.method == "POST":
        project.skills.add(skill)
        return Response(SkillSerializer(project.skills.all(), many=True).data)

    project.skills.remove(skill)
    return Response(status=status.HTTP_204_NO_CONTENT)
