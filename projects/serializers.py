from django.utils import timezone
from rest_framework import serializers

from .models import Bid, Project


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "title", "description", "budget", "deadline", "status", "client", "created_at"]
        read_only_fields = ["id", "status", "client", "created_at"]

    def validate_deadline(self, value):
        if value < timezone.localdate():
            raise serializers.ValidationError("Deadline must not be in the past.")
        return value


class BidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = ["id", "project", "freelancer", "price", "message", "status", "created_at"]
        read_only_fields = ["id", "project", "freelancer", "status", "created_at"]

    def validate(self, attrs):
        request = self.context.get("request")
        project = self.context.get("project")
        freelancer = self.context.get("freelancer")

        if request is None or project is None or freelancer is None:
            raise serializers.ValidationError("Project and freelancer context are required.")

        if request.user.role != "freelancer":
            raise serializers.ValidationError("Only freelancers can place bids.")

        if Bid.objects.filter(project=project, freelancer=freelancer).exists():
            raise serializers.ValidationError("You have already placed a bid on this project.")

        return attrs


class AcceptBidSerializer(serializers.Serializer):
    bid_id = serializers.IntegerField(read_only=True)
    status = serializers.CharField(read_only=True)
    project_status = serializers.CharField(read_only=True)
    contract_id = serializers.IntegerField(read_only=True)
