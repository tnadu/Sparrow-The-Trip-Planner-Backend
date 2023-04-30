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

class RatingFlagAuthorization(permissions.BasePermission):    
    def has_object_permission(self, request, view, obj):
        rating_flag = RatingFlag.objects.get(pk = obj.id)
        
        # if it's a rating on an attraction, check if the user is authenticated
        # else if it's a rating on a route, check the permission for that route (public/private)
        if view.action in ['list','create']:
            if rating_flag.attraction:
                return request.user.is_authenticated
            else:
                return (RouteIsPublic().has_object_permission(request, view, rating_flag.route))
        
        # only the user who rated the object is allowed to update/delete  
        if view.action in ['update','partial_update','destroy']:
            if rating_flag.attraction or rating_flag.route:
                return (IsOwnedByTheUserMakingTheRequest().has_object_permission(request, view, rating_flag))