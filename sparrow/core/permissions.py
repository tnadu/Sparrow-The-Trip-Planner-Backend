from rest_framework import permissions
from .models import *


class IsTheUserMakingTheRequest(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.baseUser
