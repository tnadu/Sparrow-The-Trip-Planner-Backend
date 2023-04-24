from rest_framework import permissions
from models import *

class IsInGroup(permissions.BasePermission):    
    def has_object_permission(self, request, view, obj):
        # when the user is trying to retrieve information about a group
        # we should check if it belongs to the group
        if request.method == 'GET':
            mebmer_id = request.user.id
            group_id = obj.id

            try:
                is_in_group = BelongsTo.objects.get(user_id = mebmer_id, group_id = group_id)
                return True
            except BelongsTo.DoesNotExist:
                return False

        # if he tries other actions, they will be denied, only
        return False