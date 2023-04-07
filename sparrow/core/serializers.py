from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *


class WriteRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ['title', 'description', 'verified', 'public', 'startingPointLat', 'startingPointLon', 'user', 'group']


# used in 'LargeUserSerializer' and 'LargeGroupSerializer'
class ExtraSmallRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ['title', 'description']


# class IsWithinSerializer(serializers.ModelSerializer):
#     attraction = SmallAttractionSerializer()
    
#     class Meta:
#         model = isWithin
#         fields = ['orderNumber', 'attraction']


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


class RegisterUserSerializer(serializers.ModelSerializer):
    passwordCheck = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'passwordCheck', 'first_name', 'last_name', 'email']
        extra_kwargs = {'passwordCheck': {'write_only': True}}

    def save(self, **kwargs):
        password = self.validated_data['password']
        passwordCheck = self.validated_data['passwordCheck']

        if password != passwordCheck:
            raise serializers.ValidationError({'password': 'Passwords must match!'})
        
        user = User(username=self.validated_data['username'], 
                    first_name=self.validated_data['first_name'], 
                    last_name=self.validated_data['last_name'],
                      email=self.validated_data['email'])
        
        user.set_password(password)
        user.save()
        return user


# read-only, nestable serializer
class SmallMemberSerializer(serializers.ModelSerializer):
    baseUser = SmallUserSerializer(read_only=True)

    class Meta:
        model = Member
        fields = ['baseUser', 'profilePhoto', 'birthDate']


# used for put/patch/delete on the Member model
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


class RegisterMemberSerializer(serializers.ModelSerializer):
    baseUser = RegisterUserSerializer()

    class Meta:
        model = Member
        fields = ['baseUser', 'profilePhoto', 'birthDate']

    def save(self, **kwargs):
        baseUserData = self.validated_data['baseUser']
        baseUserSerializer = RegisterUserSerializer(data=baseUserData)
        baseUserSerializer.is_valid(raise_exception=True)
        baseUser = baseUserSerializer.save()

        member = Member(
            baseUser=baseUser,
            profilePhoto=self.validated_data.pop('profilePhoto', None),
            birthDate=self.validated_data['birthDate']
        )

        member.save()
        return member


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
