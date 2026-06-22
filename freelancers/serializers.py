from rest_framework import serializers

from contracts.models import Review
from users.models import User


class FreelancerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "bio", "created_at"]
        read_only_fields = fields


class FreelancerReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.CharField(source="contract.client.username", read_only=True)
    reviewer_id = serializers.IntegerField(source="contract.client.id", read_only=True)

    class Meta:
        model = Review
        fields = ["id", "reviewer", "reviewer_id", "rating", "comment", "created_at"]
        read_only_fields = fields
