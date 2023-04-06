from rest_framework.viewsets import ModelViewSet
from rest_framework import status, permissions
from .models import Member, Group
from .serializers import SmallMemberSerializer, SmallGroupSerializer, WriteMemberSerializer, WriteGroupSerializer


class SmallMemberViewSet(ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = SmallMemberSerializer


class GroupViewSet(ModelViewSet):
    queryset = Group.objects.all()
    
    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return SmallGroupSerializer
        return WriteGroupSerializer
        
    