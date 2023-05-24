from rest_framework import permissions
from .models import *


class IsTheUserMakingTheRequest(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.baseUser


class IsOwnedByTheUserMakingTheRequest(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.user


class IsInGroup(permissions.BasePermission):    
    def has_object_permission(self, request, view, obj):
        mebmer_id = request.user.id
        group_id = obj.id

        try:
            is_in_group = BelongsTo.objects.get(user_id = mebmer_id, group_id = group_id)
            return True
        except BelongsTo.DoesNotExist:
            return False


class IsAdminOfGroup(permissions.BasePermission):    
    def has_object_permission(self, request, view, obj):
        mebmer_id = request.user.id
        group_id = obj.id

        try:
            is_in_group = BelongsTo.objects.get(member_id = mebmer_id, group_id = group_id)
            # if the user is an admin, the instance should have isAdmin set to true
            return is_in_group.isAdmin
        
        except BelongsTo.DoesNotExist:
            return False


class RouteIsPublic(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        publicCondition = obj.public and permissions.IsAuthenticated().has_permission(request, view)

        # current route is owned be the user making the request
        userCondition = obj.user and IsOwnedByTheUserMakingTheRequest().has_object_permission(request, view, obj)
        # current route is owned by a group to which the user making the request belongs
        groupCondition = obj.group and IsInGroup().has_object_permission(request, view, obj.group)
        privateCondition = not obj.public and (userCondition or groupCondition)

        return publicCondition or privateCondition
