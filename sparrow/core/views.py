from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status, permissions, mixins
from django.contrib.auth import login, logout
from .models import *
from .serializers import *
from .permissions import *

class RouteViewSet(ModelViewSet):
    queryset = Route.objects.all()

    # search & options for filtering and ordering
    filterset_fields = ['verified', 'user__baseUser__username', 'user__baseUser__first_name', 'user__baseUser__last_name',
                        'group__name', 'isWithin__attraction__name', 'isWithin__attraction__isTagged__tag__tagName',
                        'notebook__id', 'user', 'group', 'ratingFlag__id']
    search_fields = ['title', 'description', 'startingPointLat', 'startingPointLon']

    def get_serializer_class(self):
        if self.action == 'list':
            return ListRouteSerializer
        return RouteSerializer
    
    def get_permissions(self):
        if self.action == 'update' or self.action == 'patch' or self.action == 'delete':
            return [RouteIsAuthorizedToMakeChanges]

        # if self.action == 'list':
        #     return SmallRouteSerializer
        # elif self.action in ['create', 'update', 'partial_update']:
        #     return RouteSerializer
        # else:
        #     return LargeRouteSerializer

    # # toggle the public field
    # # detail = True means it is applied only for an instance
    # # it will respond only to update-type requests
    # @action(detail = True, methods=['PUT', 'PATCH', 'GET'])
    # def publicToggle(self, request, pk):

    #     routeObject = self.get_object()
    #     routeObject.public = not routeObject.public

    #     serializer = RouteSerializer(routeObject, data=request.data, context={'request': request})
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()


class IsWithinViewSet(GenericViewSet, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    queryset = isWithin.objects.all()
    serializer_class = IsWithinSerializer
    filterset_fields = ['route_id', 'attraction_id']


class GroupViewSet(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    filterset_fields = ['route__id', 'belongsTo__member_id']

    def get_permissions(self):
        # if the use tries to see a group/ list of groups, check if 
        # he/she appears in the group
        if self.action == 'list' or self.action == 'retrieve':
            return [IsInGroup]

        # other actions should only be taken by admins
        return [IsAdminOfGroup]

class MemberViewSet(ModelViewSet):
    queryset = Member.objects.all()
    search_fields = ['baseUser__username', 'baseUser__first_name', 'baseUser__last_name']
    filterset_fields = ['belongsTo__group_id', 'route__id', 'ratingFlag__id']

    def get_serializer_class(self):
        if self.action == 'list':
            return SmallAndListMemberSerializer
        
        if self.action == 'retrieve':
            # only a member requesting to view their own profile can 
            # access the detailed serializer containing the email field
            if self.get_object().baseUser == self.request.user:
                return MemberSerializer
            else:
                return PrivateMemberSerializer

        if self.action == 'create':
            return RegisterMemberSerializer

        return MemberSerializer

    def get_permissions(self):
        # condition for list, retrieve goes here (IsAuthenticated)

        # anyone can register
        if self.action == 'create':
            return [permissions.AllowAny()]
        
        return [IsTheUserMakingTheRequest()]

    # custom deletion logic
    def destroy(self, request, *args, **kwargs):
        member = self.get_object()
        # delete the associated baseUser first,
        # which will delete the member in cascade
        member.baseUser.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def removeProfilePhoto(self, request, **kwargs):
        member = self.get_object()
        member.profilePhoto = defaultProfilePhoto
        member.save()
        return Response(status=status.HTTP_200_OK)
    

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


class AttractionViewSet(GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin):
    queryset = Attraction.objects.all()
    serializer_class = AttractionSerializer

    filterset_fields = ['ratingFlag__id', 'isWithin__route_id', 'isTagged__tag__tagName']
    search_fields = ['name', 'generalDescription']
    ordering_fields = ['isWithin__orderNumber']
    

class BelongsToViewSet(GenericViewSet, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    queryset = BelongsTo.objects.all()
    serializer_class = BelongsToSerializer
    filterset_fields = ['member_id', 'group_id']


### BACK-UP: for belongsTo
# class BelongsToViewSet(ModelViewSet):
#     queryset = BelongsTo.objects.all()

#     filterset_fields = ['member__baseUser__username', 'group__name', 'nickname']
#     search_fields = ['nickname']

#     def get_serializer_class(self):
#         if self.action == 'get_group_members':
#             return MemberBelongsToSerializer

#         if self.action == 'get_all_groups_for_member':
#             return GroupBelongsToSerializer
        
#         return WriteBelongsToSerializer

#     # action that will list all the users that exist 
#     # within a specified group, specification given by
#     # the group's PK
#     @action(methods=['get'])
#     def get_group_members(self, request, pk=None):
#         try:
#             group_members = BelongsTo.objects.filter(group = pk)
#             group_members_serialized = self.get_serializer(group_members, many=True)
#             return Response(group_members_serialized.data)
        
#         except BelongsTo.DoesNotExist:
#             return Response(status=status.HTTP_404_NOT_FOUND)
            
#     # action that will list all groups that a particular
#     # user is included in; identification being made with 
#     # the user's PK
#     @action(methods=['get'])
#     def get_all_groups_for_member(self, request, pk=None):
#         try: 
#             all_groups = BelongsTo.objects.filter(member = pk)
#             all_groups_serialized = self.get_serializer(all_groups, many=True)
#             return Response(all_groups_serialized.data)
        
#         except BelongsTo.DoesNotExist:
#             return Response(status=status.HTTP_404_NOT_FOUND)


class NotebookViewSet(ModelViewSet):
    queryset = Notebook.objects.all()
    filterset_fields = ["user_id"]
    permission_classes = [IsOwnedByTheUserMakingTheRequest]

    def get_serializer_class(self):
        if self.action == 'list':
            return ListNotebookSerializer
        
        return NotebookSerializer
        # if self.request.method in permissions.SAFE_METHODS:     # get, head, options
        #     # if details about a specific notebook are requested
        #     if self.action == 'retrieve':
        #         return LargeNotebookSerializer
        #     # otherwise, general information about the notebook entry is presented
        #     return SmallNotebookSerializer

        # # if a specific notebook entry is being modified
        # if self.action == 'create' or self.action == 'update':
        #     return WriteNotebookSerializer

        # return LargeNotebookSerializer

    def get_permissions(self):
        # let anyone create a notebook
        if self.action == 'create':
            return [permissions.AllowAny()]
        
        return [IsOwnedByTheUserMakingTheRequest()]

class StatusViewSet(GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = Status.objects.all()
    serializer_class = StatusSerializer
    filterset_fields = ['notebook__id']


class RatingFlagViewSet(GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin,
                                     mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    serializer_class = RatingFlagSerializer
    filterset_fields = ['route_id', 'attraction_id']

    def get_queryset(self):
        # users can create both ratings and flags (instances with a ratingFlagType greater than 5)
        if self.action == 'create':
            return RatingFlag.objects.all()
        
        # once created, the flags can't be altered, which means
        # that the query set can be limitted to ratings
        return RatingFlag.objects.filter(rating_id__lte=5)


class RatingFlagTypeViewSet(GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = RatingFlagType.objects.all()
    serializer_class = RatingFlagTypeSerializer
    filterset_fields = ['ratingFlag__id']


class TagViewSet(GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filterset_fields = ['isTagged__attraction_id']


class IsTaggedViewSet(GenericViewSet,mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin):
    queryset = IsTagged.objects.all()
    serializer_class = IsTaggedSerializer
    filterset_fields = ['attraction_id', 'tag_id']
