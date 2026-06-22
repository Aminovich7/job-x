from django.db import transaction
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import Contract
from .permissions import IsContractClient, IsContractParticipant, enforce_permission
from .serializers import CancelContractSerializer, ContractSerializer, FinishContractSerializer, ReviewSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@extend_schema(responses=ContractSerializer(many=True))
def contract_list_view(request):
    contracts = Contract.objects.filter(Q(client=request.user) | Q(freelancer=request.user))
    return Response(ContractSerializer(contracts, many=True).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@extend_schema(responses=ContractSerializer)
def contract_detail_view(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    enforce_permission(request, IsContractParticipant, contract)
    return Response(ContractSerializer(contract).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@extend_schema(request=None, responses=ContractSerializer)
def finish_contract_view(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    enforce_permission(request, IsContractClient, contract)
    serializer = FinishContractSerializer(data={}, context={"contract": contract, "request": request})
    serializer.is_valid(raise_exception=True)

    with transaction.atomic():
        contract.status = Contract.STATUS_FINISHED
        contract.finished_at = timezone.now()
        contract.project.status = "completed"
        contract.project.save(update_fields=["status"])
        contract.save(update_fields=["status", "finished_at"])

    return Response(ContractSerializer(contract).data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@extend_schema(request=ReviewSerializer, responses=ReviewSerializer)
def review_contract_view(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    enforce_permission(request, IsContractClient, contract)
    serializer = ReviewSerializer(
        data=request.data,
        context={"contract": contract, "request": request},
    )
    serializer.is_valid(raise_exception=True)
    review = serializer.save(contract=contract)
    return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@extend_schema(request=None, responses=ContractSerializer)
def cancel_contract_view(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    enforce_permission(request, IsContractParticipant, contract)
    serializer = CancelContractSerializer(data={}, context={"contract": contract, "request": request})
    serializer.is_valid(raise_exception=True)

    with transaction.atomic():
        contract.status = Contract.STATUS_CANCELLED
        contract.save(update_fields=["status"])
        contract.project.status = "cancelled"
        contract.project.save(update_fields=["status"])

    return Response(ContractSerializer(contract).data, status=status.HTTP_200_OK)
