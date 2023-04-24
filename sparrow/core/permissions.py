from rest_framework import permissions
from .models import *


class IsWithinAuthorization(permissions.BasePermission):
    # will validate 'create' requests
    def has_permission(self, request, view):
        # access the serialized and validated IsWithin data
        validatedIsWithinData = view.get_serializer().context['data']
        route = Route.objects.get(pk=validatedIsWithinData['route_id'])

        return RouteIsAuthorizedToMakeChanges().has_object_permission(request, view, route)

    # validates all other allowed actions
    def has_object_permission(self, request, view, obj):
        route = Route.objects.get(pk=obj.route_id)

        if view.action == 'retrieve':
            return RouteIsPublic().has_object_permission(request, view, route)
        
        return RouteIsAuthorizedToMakeChanges().has_object_permission(request, view, route)
