from rest_framework import permissions
from django.contrib.auth.models import User

class IsOwnerOrReadonly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if isinstance(obj, User):
            return request.user == obj
        return request.user == obj.user

class IsOwner(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, User):
            return request.user == obj
        return request.user == obj.user