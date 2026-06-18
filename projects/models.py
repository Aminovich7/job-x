from django.conf import settings
from django.db import models


class Project(models.Model):
    STATUS_OPEN = "open"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_OPEN, "open"),
        (STATUS_IN_PROGRESS, "in_progress"),
        (STATUS_COMPLETED, "completed"),
        (STATUS_CANCELLED, "cancelled"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    budget = models.DecimalField(max_digits=12, decimal_places=2)
    deadline = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="projects",
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)


class Bid(models.Model):
    STATUS_PENDING = "pending"
    STATUS_ACCEPTED = "accepted"
    STATUS_REJECTED = "rejected"
    STATUS_CHOICES = [
        (STATUS_PENDING, "pending"),
        (STATUS_ACCEPTED, "accepted"),
        (STATUS_REJECTED, "rejected"),
    ]

    project = models.ForeignKey(Project, related_name="bids", on_delete=models.CASCADE)
    freelancer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="bids",
        on_delete=models.CASCADE,
    )
    price = models.DecimalField(max_digits=12, decimal_places=2)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["project", "freelancer"],
                name="unique_bid_per_freelancer_per_project",
            )
        ]
