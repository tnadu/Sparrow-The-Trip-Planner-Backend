from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, mixins
from django.contrib.auth import login, logout
from django.db.models import Prefetch
from .models import *
from .serializers import *
from django.http import Http404
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action



class RouteViewSet(ModelViewSet):
    queryset = Route.objects.all()

    # search & options for filtering and ordering
    filterset_fields = ['verified', 'user__baseUser__username', 'user__baseUser__first_name', 'user__baseUser__last_name',
                        'group__name', 'isWithin__attraction__name', 'isWithin__attraction__isTagged__tag__tagName']
    search_fields = ['title', 'description', 'startingPointLat', 'startingPointLon']
    ordering_fields = ['startingPointLat', 'startingPointLon']


    # obtain the object that will be used
    def get_object(self, pk):
        try:
            return Route.objects.get(pk=pk)
        except Route.DoesNotExist:
            raise Http404

    # depending of the type of request, a specific Serializer will be used
    def get_serializer_class(self):
        if self.action == 'list':
            return SmallRouteSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return WriteRouteSerializer
        else:
            return LargeRouteSerializer

    # toggle the verify field, only the admin can do this
    # detail = True means it is applied only for an instance
    @action(detail = True, methods=['PUT', 'PATCH'], permission_classes=[IsAdminUser])
    def verifiy(self, request, pk):

        routeObject = self.get_object(pk)

        if(routeObject.verified == True):
            routeObject.verified = False
        else: routeObject.verified = True

        serializer = WriteRouteSerializer(routeObject)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# rough idea of the ViewSets associated with a Member and a Group
class GroupViewSet(ModelViewSet):
    queryset = Group.objects.all()
    
    # different serializers for different actions
    def get_serializer_class(self):
        # get, head, options methods
        if self.request.method in permissions.SAFE_METHODS:
            return SmallGroupSerializer
        return WriteGroupSerializer


class MemberViewSet(ModelViewSet):
    queryset = Member.objects.prefetch_related(
        Prefetch('ratings', queryset=Rating.objects.filter(rating > 0), to_attr='filtered_ratings'))

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return SmallMemberSerializer
        
        if self.action == 'create':
            return RegisterMemberSerializer

        return WriteMemberSerializer

    # custom deletion logic
    def destroy(self, request, *args, **kwargs):
        member = self.get_object()
        # delete the associated baseUser first,
        # which will delete the member in cascade
        member.baseUser.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

# none of the default actions will be performed using
# this ViewSet, so a GenericViewSet is better suited
class LoginViewSet(GenericViewSet):
    queryset = User.objects.all()
    serializer_class = LoginSerializer

    # action associated with the POST method, which manages the login process
    def post(self, request):
        # validating the provided credentials using the associated serializer
        userSerializer = LoginSerializer(data=request.data, context={'request': request})
        userSerializer.is_valid(raise_exception=True)
        
        user = userSerializer.validated_data['user']
        # the validated user gets logged in, which means that
        # the response header will contain a session_id cookie
        login(self.request, user)
        return Response(None, status=status.HTTP_202_ACCEPTED)


# since it is not necessary for a serializer or a model to be
# associated with the logout action, an APIView will suffice
class LogoutView(APIView):
    def post(self, request):
        logout(request)     # django handles the logout procedure
        return Response(None, status=status.HTTP_204_NO_CONTENT)


# since only the update action will be performed, a mixin is used
class ChangePasswordViewSet(mixins.UpdateModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = ChangePasswordSerializer


class AttractionViewSet(ModelViewSet):
    # prefetch only related rating instances with a rating greater than 0 (i.e. not a flag)
    queryset = Attraction.objects.prefetch_related(
        Prefetch('ratings', queryset=Rating.objects.filter(rating > 0), to_attr='filtered_ratings'))
    serializer_class = LargeAttractionSerializer

    filterset_fields = ['tag__tagName']
    search_fields = ['name', 'generalDescription']
    