from rest_framework import permissions
from main.models import UserSubscriptions, Subscription


class MyPermissionIsAdminOrOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj in Subscription.objects.filter(id__in=UserSubscriptions.objects.get(user=request.user).subscriptions.all()):
            return True
        return bool(request.user and request.user.is_staff)
