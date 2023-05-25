from rest_framework import permissions
from .serializers import BelongsToSerializer, RatingFlagSerializer, IsWithinSerializer
from .models import *


class IsTheUserMakingTheRequest(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.baseUser


class IsOwnedByTheUserMakingTheRequest(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.user.baseUser


class IsInGroup(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user_id = request.user.id
        group_id = obj.id

        try:
            is_in_group = BelongsTo.objects.get(user_id = user_id, group_id = group_id)
            return True
        except BelongsTo.DoesNotExist:
            return False


class IsAdminOfGroup(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user_id = request.user.id
        group_id = obj.id

        try:
            is_in_group = BelongsTo.objects.get(user_id = user_id, group_id = group_id)
            # if the user is an admin, the instance should have isAdmin set to true
            return is_in_group.isAdmin

        except BelongsTo.DoesNotExist:
            return False


class BelongsToAuthorization(permissions.BasePermission):
    def has_permission(self, request, view):
        # allows all other actions, since they will be checked
        # individually in the has_object_permission method
        if view.action != 'create':
            return True

        # the request data is not validated against the corresponding
        # serializer before the permission checking, and since whether
        # or not the user is allowed to use this action depends upon
        # the validity of the data, it is serialized on the fly
        serializer = BelongsToSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        group = data['group']
        nickname = data.get('nickname')

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
        return IsAdminOfGroup().has_object_permission(request, view, group)

    def has_object_permission(self, request, view, obj):
        group = Group.objects.get(pk=obj.group_id)

        if view.action == 'destroy':
            isAdmin = IsAdminOfGroup().has_object_permission(request, view, group)
            userToBeModified = Member.objects.get(pk=obj.user_id)
            theirOwnEntry = IsTheUserMakingTheRequest().has_object_permission(request, view, userToBeModified)

            return isAdmin or theirOwnEntry

        # 'update' and 'partial_update' action section
        user = request.data.get('user')
        groupInRequest = request.data.get('group')
        nickname = request.data.get('nickname')
        isAdmin = request.data.get('isAdmin')

        modifiedUser = Member.objects.get(pk=obj.user_id)

        # in order to replace a user in a group or move a user in another
        # group, the 'create' and 'delete' actions will be used instead
        if user or groupInRequest:
            return False

        # only admins can change the admin status of other group members
        if isAdmin and not IsAdminOfGroup().has_object_permission(request, view, group):
            return False

        # any group member can change their nickname, as long as it's theirs
        if nickname and not IsTheUserMakingTheRequest().has_object_permission(request, view, modifiedUser):
            return False

        return True


class RouteIsAuthorizedToMakeChanges(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # current route is owned be the user making the request
        userCondition = obj.user and IsOwnedByTheUserMakingTheRequest().has_object_permission(request, view, obj)
        # current route is owned by a group to which the user making the request belongs
        groupCondition = obj.group and IsInGroup().has_object_permission(request, view, obj.group)

        return userCondition or groupCondition


class RouteIsPublic(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        publicCondition = obj.public and permissions.IsAuthenticated().has_permission(request, view)

        return publicCondition or RouteIsAuthorizedToMakeChanges().has_object_permission(request, view, obj)


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


class IsWithinAuthorization(permissions.BasePermission):
    # will validate 'create' requests
    def has_permission(self, request, view):
        if view.action != 'create':
            return True

        serializer = IsWithinSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        route = Route.objects.get(pk=data['route'])

        return RouteIsAuthorizedToMakeChanges().has_object_permission(request, view, route)

    # validates all other allowed actions
    def has_object_permission(self, request, view, obj):
        route = Route.objects.get(pk=obj.route_id)

        return RouteIsAuthorizedToMakeChanges().has_object_permission(request, view, route)
