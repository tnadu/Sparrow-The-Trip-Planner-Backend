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
        member_id = request.user.id
        group_id = obj.id

        try:
            is_in_group = BelongsTo.objects.get(user_id = member_id, group_id = group_id)
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
        

class BelongsToAuthorization(permissions.BasePermission):
    def has_permission(self, request, view):
        validatedBelongsToData = view.get_serializer().context.get('data')
        group = Group.objects.get(pk=validatedBelongsToData['group_id'])

        return IsAdminOfGroup().check_object_permissions(request, group)
    
    def has_object_permission(self, request, view, obj):
        group = Group.objects.get(pk=obj.group_id)
        
        if view.action == 'retrieve':
            return IsInGroup().check_object_permissions(request, group)
        
        if view.action == 'destroy':
            return IsAdminOfGroup().check_object_permissions(request, group)
        
        # 'update' and 'partial_update' action section
        nickname = request.data.get('nickname')
        modifiedUser = User.objects.get(pk=obj.user_id)

        if nickname:
            return IsTheUserMakingTheRequest().check_object_permissions(request, modifiedUser)

        isAdmin = request.data.get('isAdmin')

        if isAdmin:
            return IsAdminOfGroup().check_object_permissions(request, group)
        
        return True

