from rest_framework import permissions


class IsClient(permissions.BasePermission):
    """
    Allow access only to users with the CLIENT role.
    Used for the Create action — only clients can post new projects.
    """

    message = "Only client accounts can create projects."

    def has_permission(self, request, view):
        # SAFE_METHODS (GET, HEAD, OPTIONS) can pass through;
        # this permission is meant to be combined with others for write actions.
        if not request.user or not request.user.is_authenticated:
            return False
        return getattr(request.user, "role", None) == "CLIENT"


class IsOwner(permissions.BasePermission):
    """
    Object-level permission: only the project's owner can
    retrieve/update/delete it when it's not publicly viewable.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            # Read access to non-owners is handled separately
            # (e.g. only if project.status == OPEN), not here.
            return obj.owner_id == request.user.id or obj.status == obj.Status.OPEN
        # Write methods (PATCH, PUT, DELETE) — owner only
        return obj.owner_id == request.user.id
    
class IsFreelancer(permissions.BasePermission):
    """
    Allow access only to users with the FREELANCER role.
    Used for the Proposal Create action.
    """

    message = "Only freelancer accounts can submit proposals."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return getattr(request.user, "role", None) == "FREELANCER"
    
from rest_framework import permissions


class IsProposalOwnerPending(permissions.BasePermission):
    """
    Object-level permission for Proposal update/delete:
    - Only the freelancer who submitted it
    - Only while status is still PENDING
    """

    message = "You can only edit your own proposal while it is still pending."

    def has_object_permission(self, request, view, obj):
        if obj.freelancer_id != request.user.id:
            return False
        return obj.status == obj.Status.PENDING