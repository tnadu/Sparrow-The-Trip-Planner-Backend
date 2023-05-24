from rest_framework import permissions
from .serializers import RatingFlagSerializer
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
    # necessary for the 'create' action
    def has_permission(self, request, view):
        if view.action != 'create':
            return True

        serializer = RatingFlagSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # the rating is associated with an attraction
        if data.get('attraction'):
            return permissions.IsAuthenticated().has_permission(request, view)

        # the rating is associated with a route
        return RouteIsPublic().has_object_permission(request, view, data['route'])


    def has_object_permission(self, request, view, obj):
        # a user can interact with the ratings associated with a given route only if the route is public
        if obj.route and not RouteIsPublic().has_object_permission(request, view, obj.route):
            return False

        if view.action == 'list':
            if obj.attraction:
                return permissions.IsAuthenticated().has_permission(request, view)

            # the rating is associated with a route which is
            # visible to the user, which makes it visible too
            return True
        
        # only the user who posted a rating is allowed to modify/delete it
        return IsTheUserMakingTheRequest().has_object_permission(request, view, obj.user)
