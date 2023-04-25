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

        group_id = validatedBelongsToData['group_id']
        nickname = validatedBelongsToData.get('nickname')

        # since the provided data passed the serializer validation,
        # it is guaranteed that when a group admin creates a new entry
        # in the BelongsTo model, the unique (group, user) constraint
        # would be violated if they tried to enter their own id in the
        # user field;
        # this means that whenever a nickname is provided, it is related
        # to another user, which is forbidden; 
        if nickname:
            return False

        # a request is authorized only if it is issued by a group admin
        group = Group.objects.get(pk=group_id)
        return IsAdminOfGroup().check_object_permissions(request, group)
    
    def has_object_permission(self, request, view, obj):
        group = Group.objects.get(pk=obj.group_id)
        
        if view.action == 'retrieve':
            return IsInGroup().check_object_permissions(request, group)
        
        if view.action == 'destroy':
            isAdmin = IsAdminOfGroup().check_object_permissions(request, group)
            userToBeModified = Member.objects.get(pk=obj.user_id)
            theirOwnEntry = IsTheUserMakingTheRequest().check_object_permissions(request, userToBeModified)

            return isAdmin or theirOwnEntry
        
        # 'update' and 'partial_update' action section
        user_id = request.data.get('user_id')
        group_id = request.data.get('group_id')
        nickname = request.data.get('nickname')
        isAdmin = request.data.get('isAdmin')
        
        modifiedUser = User.objects.get(pk=obj.user_id)

        # in order to replace a user in a group or move a user in another
        # group, the 'create' and 'delete' actions will be used instead
        if user_id or group_id:
            return False

        # only admins can change the admin status of other group members
        if isAdmin and not IsAdminOfGroup().check_object_permissions(request, group):
            return False

        # any group member can change their nickname, as long as it's theirs
        if nickname and not IsTheUserMakingTheRequest().check_object_permissions(request, modifiedUser):
            return False

        return True
    
