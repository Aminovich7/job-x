from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission


def enforce_permission(request, permission_class, obj=None):
    permission = permission_class()
    if not permission.has_permission(request, None):
        raise PermissionDenied(getattr(permission, "message", "Permission denied."))
    if obj is not None and hasattr(permission, "has_object_permission"):
        if not permission.has_object_permission(request, None, obj):
            raise PermissionDenied(getattr(permission, "message", "Permission denied."))


class IsClient(BasePermission):
    message = "Only clients are allowed to perform this action."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "client"


class IsFreelancer(BasePermission):
    message = "Only freelancers are allowed to perform this action."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "freelancer"


class IsAuthenticatedClientWrite(BasePermission):
    message = "Only clients can perform write actions here."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method == "POST":
            return request.user.role == "client"
        return True


class IsAuthenticatedFreelancerBidWrite(BasePermission):
    message = "Only freelancers can place bids."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method == "POST":
            return request.user.role == "freelancer"
        return True


class IsProjectOwner(BasePermission):
    message = "Only the project owner can perform this action."

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.client == request.user
