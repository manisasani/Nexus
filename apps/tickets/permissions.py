from rest_framework import permissions


class IsStaffUser(permissions.BasePermission):
    message = "Only support staff can perform this action."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class IsTicketOwnerOrStaff(permissions.BasePermission):
    """
    Object-level: only the ticket's opener or staff can view/interact with it.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.opened_by_id == request.user.id