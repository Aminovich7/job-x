from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission


def enforce_permission(request, permission_class, obj=None):
    permission = permission_class()
    if not permission.has_permission(request, None):
        raise PermissionDenied(getattr(permission, "message", "Permission denied."))
    if obj is not None and hasattr(permission, "has_object_permission"):
        if not permission.has_object_permission(request, None, obj):
            raise PermissionDenied(getattr(permission, "message", "Permission denied."))


class IsContractParticipant(BasePermission):
    message = "Only the client or freelancer on this contract can access it."

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user in (obj.client, obj.freelancer)


class IsContractClient(BasePermission):
    message = "Only the client can perform this action."

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user == obj.client
