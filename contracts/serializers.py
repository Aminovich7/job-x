from rest_framework import serializers

from projects.models import Project
from users.models import User

from .models import Contract, Review


class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = [
            "id",
            "project",
            "client",
            "freelancer",
            "agreed_price",
            "status",
            "created_at",
            "finished_at",
        ]
        read_only_fields = fields


class FinishContractSerializer(serializers.Serializer):
    def validate(self, attrs):
        contract = self.context.get("contract")

        if contract is None:
            raise serializers.ValidationError("Contract context is required.")

        if contract.status != Contract.STATUS_ACTIVE:
            raise serializers.ValidationError("Contract must be active.")

        return attrs


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["id", "contract", "rating", "comment", "created_at"]
        read_only_fields = ["id", "contract", "created_at"]

    def validate(self, attrs):
        contract = self.context.get("contract")

        if contract is None:
            raise serializers.ValidationError("Contract context is required.")

        if contract.status != Contract.STATUS_FINISHED:
            raise serializers.ValidationError("Contract must be finished.")

        if Review.objects.filter(contract=contract).exists():
            raise serializers.ValidationError("A review already exists for this contract.")

        return attrs


class CancelContractSerializer(serializers.Serializer):
    def validate(self, attrs):
        contract = self.context.get("contract")

        if contract is None:
            raise serializers.ValidationError("Contract context is required.")

        if contract.status != Contract.STATUS_ACTIVE:
            raise serializers.ValidationError("Contract must be active.")

        return attrs


class CreateContractSerializer(serializers.Serializer):
    project_id = serializers.IntegerField()
    freelancer_id = serializers.IntegerField()
    agreed_price = serializers.DecimalField(max_digits=12, decimal_places=2)

    def validate_project_id(self, value):
        try:
            project = Project.objects.get(id=value)
        except Project.DoesNotExist:
            raise serializers.ValidationError("Project not found.")
        if project.status != Project.STATUS_OPEN:
            raise serializers.ValidationError("Project must be open.")
        if Contract.objects.filter(project=project).exists():
            raise serializers.ValidationError("A contract already exists for this project.")
        return value

    def validate_freelancer_id(self, value):
        try:
            user = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")
        if user.role != User.ROLE_FREELANCER:
            raise serializers.ValidationError("User is not a freelancer.")
        return value

    def validate_agreed_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        project = Project.objects.get(id=attrs["project_id"])

        if project.client != request.user:
            raise serializers.ValidationError("You can only create contracts for your own projects.")

        return attrs
