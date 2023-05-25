from rest_framework import permissions
from .serializers import IsWithinSerializer
from .models import *


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
