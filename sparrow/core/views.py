from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.response import Response
from rest_framework import status, permissions, mixins
from .models import Member, Group
from .serializers import *


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
    queryset = Member.objects.all()

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
    

# since only the update action will be performed, a mixin is used
class ChangePasswordViewSet(mixins.UpdateModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = ChangePasswordSerializer
