from rest_framework import permissions
from .models import *

class IsTheUserMakingTheRequest(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.baseUser

class IsAdminOfGroup(permissions.BasePermission):    
    def has_object_permission(self, request, view, obj):
        # when the user is trying to perform action on a group
        # we should check if it belongs to the group
        if request.method == 'POST' or request.method == 'PUT' or request.method == 'PATCH' or request.method == 'DELETE':
            mebmer_id = request.user.id
            group_id = obj.id

            try:
                is_in_group = BelongsTo.objects.get(member_id = mebmer_id, group_id = group_id)
                # if the user is admin, it should have isAdmin set to true
                return is_in_group.isAdmin
            
            except BelongsTo.DoesNotExist:
                return False

        # if he tries other actions, they will be denied, only
        return False

