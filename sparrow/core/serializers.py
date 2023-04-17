from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Member, Group, Route, isWithin, Attraction

#used for write operations (post/put)
class WriteRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ['title', 'description', 'verified', 'public', 'startingPointLat', 'startingPointLon', 'user', 'group']

# retreives all the information for a a route
class LargeRouteSerializer(serializers.ModelSerializer):

    author = SmallUserSerializer()
    is_within = IsWithinSerializer(many=True) # one for each attraction of the route
    group = SmallGroupSerializer()

    class Meta:
        model = Route
        fields = ['title', 'description', 'verified', 'public', 'startingPointLat', 'startingPointLon', 'publicationDate',
                  'author', 'is_within', 'group']

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

# retrieves ALL the information about an attraction
class LargeAttractionSerializer(serializers.ModelSerializer):
    tag = SmallTagSerializer()
    rating = RatingSerializer()

    class Meta:
        model = Attraction
        fields = ['name', 'generalDescription', 'photo', 'latitude', 'longitude', 'tag', 'rating']
