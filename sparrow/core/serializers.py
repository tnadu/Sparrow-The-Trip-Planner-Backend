from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Member, Group, Route

#used for write operations (post/put)
class WriteRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ['title', 'description', 'verified', 'public', 'startingPointLat', 'startingPointLon', 'user', 'group']


# used in 'LargeUserSerializer' and 'LargeGroupSerializer'
class ExtraSmallRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ['title', 'description']

# returns concise information about the attractions of a particular route:
class IsWithinSerializer(serializers.ModelSerializer):

    attraction = SmallAttractionSerializer()
    class Meta:
        model = IsWithin
        fields = ['orderNumber', 'attraction']

# used for write operations(put, post)
class WriteIsWithinSerializer(serializers.ModelSerializer):
    class Meta:
        model = IsWithin
        fields = ['route', 'attraction', 'orderNumber']


# used in 'LargeMemberSerializer' and 'WriteMemberSerializer'
class LargeUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


# nested in 'SmallMemberSerializer'
class SmallUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']


# read-only, nestable serializer
class SmallMemberSerializer(serializers.ModelSerializer):
    baseUser = SmallUserSerializer(read_only=True)

    class Meta:
        model = Member
        fields = ['baseUser', 'profilePhoto', 'birthDate']


# read-only, nestable serializer
class SmallGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name']
