from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from projects.models import Project


class Contract(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_FINISHED = "finished"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "active"),
        (STATUS_FINISHED, "finished"),
        (STATUS_CANCELLED, "cancelled"),
    ]

    project = models.OneToOneField(Project, on_delete=models.CASCADE)
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="client_contracts",
        on_delete=models.CASCADE,
    )
    freelancer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="freelancer_contracts",
        on_delete=models.CASCADE,
    )
    agreed_price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)


class Review(models.Model):
    contract = models.OneToOneField(Contract, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
