from rest_framework import serializers

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
        request = self.context.get("request")

        if contract is None or request is None:
            raise serializers.ValidationError("Contract context is required.")

        if contract.status != Contract.STATUS_ACTIVE:
            raise serializers.ValidationError("Contract must be active.")

        if request.user != contract.client:
            raise serializers.ValidationError("Only the client can finish the contract.")

        return attrs


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["id", "contract", "rating", "comment", "created_at"]
        read_only_fields = ["id", "contract", "created_at"]

    def validate(self, attrs):
        contract = self.context.get("contract")
        request = self.context.get("request")

        if contract is None or request is None:
            raise serializers.ValidationError("Contract context is required.")

        if contract.status != Contract.STATUS_FINISHED:
            raise serializers.ValidationError("Contract must be finished.")

        if request.user != contract.client:
            raise serializers.ValidationError("Only the client can review the contract.")

        if Review.objects.filter(contract=contract).exists():
            raise serializers.ValidationError("A review already exists for this contract.")

        return attrs


class CancelContractSerializer(serializers.Serializer):
    def validate(self, attrs):
        contract = self.context.get("contract")
        request = self.context.get("request")

        if contract is None or request is None:
            raise serializers.ValidationError("Contract context is required.")

        if contract.status != Contract.STATUS_ACTIVE:
            raise serializers.ValidationError("Contract must be active.")

        if request.user not in (contract.client, contract.freelancer):
            raise serializers.ValidationError("Only the client or freelancer can cancel the contract.")

        return attrs
