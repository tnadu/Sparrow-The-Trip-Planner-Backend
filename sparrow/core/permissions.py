from rest_framework import permissions
from .models import *


class IsWithinAuthorization(permissions.BasePermission):
    def has_permission(self, request, view):
        

    def has_object_permission(self, request, view, obj):
        route = Route.objects.get(pk=obj.route_id)

        if view.action == 'retrieve':
            return RouteIsPublic().has_object_permission(request, view, route)
        
        return RouteIsAuthorizedToMakeChanges().has_object_permission(request, view, route)
