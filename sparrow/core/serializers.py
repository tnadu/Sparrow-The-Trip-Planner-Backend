from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Member, Group, Route


class WriteRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ['title', 'description', 'verified', 'public', 'startingPointLat', 'startingPointLon', 'user', 'group']


# used in 'LargeUserSerializer' and 'LargeGroupSerializer'
class ExtraSmallRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ['title', 'description']


class IsWithinSerializer(serializers.ModelSerializer):
    attraction = SmallAttractionSerializer()
    
    class Meta:
        model = IsWithin
        fields = ['orderNumber', 'attraction']


# used in 'LargeMemberSerializer' and 'WriteMemberSerializer'
class LargeUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


# nested in 'SmallMemberSerializer'
class SmallUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


# read-only, nestable serializer
class SmallMemberSerializer(serializers.ModelSerializer):
    baseUser = SmallUserSerializer(read_only=True)

    class Meta:
        model = Member
        fields = ['baseUser', 'profilePhoto', 'birthDate']


# used for post/put/patch/delete on the Member model
class WriteMemberSerializer(serializers.ModelSerializer):
    baseUser = LargeUserSerializer()

    class Meta:
        model = Member
        fields = ['baseUser', 'profilePhoto', 'birthDate']

    # custom update method, for updating the related user
    # with the corresponding validated data, before updating
    # their associated member
    def update(self, instance, validated_data):
        # extract validated user data
        extractedUserData = validated_data.pop('baseUser', None)

        if extractedUserData:
            # aquire instance
            currentBaseUser = instance.baseUser
            # serialize and verify the validated user data
            currentBaseUserSerializer = LargeUserSerializer(currentBaseUser, data=extractedUserData, partial=True)
            currentBaseUserSerializer.is_valid(raise_exception=True)
            # save the changes
            currentBaseUserSerializer.save()
        
        # update the member itself
        return super().update(instance, validated_data)


# read-only, nestable serializer
class SmallGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name']


# used for post/put/patch/delete on the Group model
class WriteGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name', 'description']
