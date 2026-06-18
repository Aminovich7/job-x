from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CLIENT = "client"
    ROLE_FREELANCER = "freelancer"
    ROLE_CHOICES = [
        (ROLE_CLIENT, "client"),
        (ROLE_FREELANCER, "freelancer"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
