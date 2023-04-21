from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from .models import *
from datetime import date


# used in 'LargeMemberSerializer' and 'WriteMemberSerializer'
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


# nested in 'SmallMemberSerializer'
class PrivateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']

# useful for Route, Rating to display the name of the creator
class SmallUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class RegisterUserSerializer(serializers.ModelSerializer):
    passwordCheck = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'passwordCheck', 'first_name', 'last_name', 'email']
        extra_kwargs = {'passwordCheck': {'write_only': True}}

    # custom save method logic, to accommodate password 
    # matching and properly setting the validated password
    def save(self, **kwargs):
        password = self.validated_data['password']
        passwordCheck = self.validated_data['passwordCheck']

        # the two passwords fields must match
        if password != passwordCheck:
            raise serializers.ValidationError({'password': 'Passwords must match!'})
        
        # email can be neither null, nor blank
        if self.validated_data.get('email') is None or self.validated_data['email'] == '':
            raise serializers.ValidationError({'email': 'Email field is required.'})

        # creating instance of User Model
        user = User(username=self.validated_data['username'], 
                    # first and last names can be blank
                    first_name=self.validated_data.pop('first_name', ''), 
                    last_name=self.validated_data.pop('last_name', ''),
                    email=self.validated_data.pop('email'))
        
        # properly setting the password
        user.set_password(password)
        user.save()
        return user


# a regular Serializer is used, so that no 'create'-related validations or
# any other default behaviour of a ModelSerializer pollute the POST request
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(label='Username', write_only=True)
    password = serializers.CharField(label='Password', style={'input_type': 'password'}, trim_whitespace=False, write_only=True)

    def validate(self, attrs):      # overwritten
        username = attrs['username']
        password = attrs['password']

        if not username or not password:
            raise serializers.ValidationError({'authorization': 'Both "username" and "password" are required!'})
        
        # using the built-in django method for authentication
        user = authenticate(request=self.context['request'], username=username, password=password)

        if not user:
            raise serializers.ValidationError({'authorization': 'Invalid username or password!'})
        
        # the user is properly validated, which means it can be 
        # placed in the serializer's validated_data attribute
        attrs['user'] = user
        return attrs


class ChangePasswordSerializer(serializers.ModelSerializer):
    newPassword = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['password', 'newPassword']

    # custom update method for password checking and newPassword validation
    def update(self, instance, validated_data):
        password = validated_data['password']
        updatedPassword = validated_data['newPassword']

        # make sure provided current password is valid
        if not check_password(password, instance.password):
            raise serializers.ValidationError({'password': 'Incorrect password.'})

        # validate provided new password
        try:
            validate_password(updatedPassword)
        except Exception as invalidPassword:
            raise serializers.ValidationError({'newPassword': invalidPassword})

        instance.set_password(updatedPassword)
        instance.save()
        return instance


class RegisterMemberSerializer(serializers.ModelSerializer):
    baseUser = RegisterUserSerializer()

    class Meta:
        model = Member
        fields = ['baseUser', 'profilePhoto', 'birthDate']

    # custom save method, so that a baseUser can be instantiated
    # before the Member instance itself;
    def save(self, **kwargs):
        baseUserData = self.validated_data['baseUser']
        # creating serializer based on validated data
        baseUserSerializer = RegisterUserSerializer(data=baseUserData)
        # validating said data
        baseUserSerializer.is_valid(raise_exception=True)
        # creating the instance
        baseUser = baseUserSerializer.save()

        member = None

        if 'profilePhoto' in self.validated_data:
            member = Member(
                baseUser=baseUser,
                profilePhoto=self.validated_data.pop('profilePhoto'),
                birthDate=self.validated_data['birthDate']
            )

            # member.save()
        else:
            member = Member(
                baseUser=baseUser,
                birthDate=self.validated_data['birthDate']
            )

        member.save()
        return member


# class LargeMemberSerializer(serializers.ModelSerializer):
#     baseUser = LargeUserSerializer(read_only=True)
#     groups = GroupBelongsToSerializer(many=True, read_only=True)
#     routes = ExtraSmallRouteSerializer(many=True, read_only=True)
#     ratings = SmallRatingSerializer(source='filtered_ratings', many=True, read_only=True)  
#     notebooks = SmallNotebookSerializer(many=True, read_only=True)

#     class Meta:
#         model = Member
#         fields = ['baseUser', 'profilePhoto', 'birthdate', 'groups', 'routes', 'ratings', 'notebooks']


# nestable serializer
class MemberSerializer(serializers.ModelSerializer):
    baseUser = UserSerializer()

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
            currentBaseUserSerializer = UserSerializer(currentBaseUser, data=extractedUserData, partial=True)
            currentBaseUserSerializer.is_valid(raise_exception=True)
            # save the changes
            currentBaseUserSerializer.save()
        
        # update the member itself
        return super().update(instance, validated_data)

class PrivateMemberSerializer(serializers.ModelSerializer):
    baseUser = PrivateUserSerializer(read_only=True)

    class Meta:
        model = Member
        fields = ['baseUser', 'profilePhoto', 'birthDate']

# for Route, to display the user's profile image & username
class SmallAndListMemberSerializer(serializers.ModelSerializer):
    baseUser = SmallUserSerializer(read_only=True)

    class Meta:
        model = Member
        fields = ['baseUser', 'profilePhoto']

#### Group #####
################

class SmallGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name', 'description']

# class LargeGroupSerializer(serializers.ModelSerializer):
#     members = MemberBelongsToSerializer(many=True, read_only=True)
#     routes = ExtraSmallRouteSerializer(many=True, read_only=True)

#     class Meta:
#         model = Group
#         fields = ['name', 'description', 'members', 'routes']

##### BelongsTo #####
#####################

class BelongsToSerializer(serializers.ModelSerializer):
    class Meta:
        model = BelongsTo
        fields = ['member', 'group', 'isAdmin', 'nickname']


# class GroupBelongsToSerializer(serializers.ModelSerializer):
#     groups = SmallGroupSerializer(many=True, read_only=True)

#     class Meta:
#         model = BelongsTo
#         fields = ['groups', 'isAdmin', 'nickname']


# class MemberBelongsToSerializer(serializers.ModelSerializer):
#     members = SmallMemberSerializer(many=True, read_only=True)
    
#     class Meta:
#         model = BelongsTo
#         fields = ['members', 'isAdmin', 'nickname']


##### Route #####
#####################
# used for write operations (post/put)
class WriteRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ['id', 'title', 'description', 'verified', 'public', 'startingPointLat', 'startingPointLon', 'user', 'group']

    def create(self, validated_data):

        group = None
        user = None

        try:
            group = validated_data.get('group')
        except: pass

        try:
            user = Member.objects.get(baseUser=validated_data.get('user'))
        except: pass

        validated_data['user'] = user
        validated_data['group'] = group

        return super().create(validated_data)

    #check if user passes ownership to the group
    def update(self, instance, validated_data):

        group = None
        user = None
        try:
            group = validated_data.get('group')
        except: pass

        try:
            user = Member.objects.get(baseUser=validated_data.get('user'))
        except: pass

        validated_data['user'] = user
        validated_data['group'] = group
        return super().update(instance, validated_data)


    # Only one and exactly one of the two nullable fields (group, user) can be null at a time.
    def validate(self, data):

        group = None
        user = None
        try:
            group = data.get('group')
        except: pass

        try:
            user = Member.objects.get(baseUser=data.get('user'))
        except: pass

        if (user is not None and group is not None) or (user is None and group is None):
            raise serializers.ValidationError("Only one of user and group can be specified")
        return data



# retreives ALL the information for a a route
class LargeRouteSerializer(serializers.ModelSerializer):
    user = SmallMemberSerializer()
    is_within = IsWithinSerializer(many=True, required=False)  # one for each attraction of the route
    group = SmallGroupSerializer()

    class Meta:
        model = Route
        fields = ['id', 'title', 'description', 'verified', 'public', 'startingPointLat', 'startingPointLon',
                  'publicationDate',
                  'user', 'is_within', 'group']


# retrieves partial information about a route
class SmallRouteSerializer(serializers.ModelSerializer):
    user = SmallMemberSerializer()
    group = SmallGroupSerializer()

    class Meta:
        model = Route
        fields = ['id', 'title', 'description', 'verified', 'public', 'user', 'group']


# used in 'LargeUserSerializer' and 'LargeGroupSerializer'
class ExtraSmallRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ['id', 'title', 'description']


#### IsWithin ####
##################

class IsWithinSerializer(serializers.ModelSerializer):
    class Meta:
        model = isWithin
        fields = ['route', 'attraction', 'orderNumber']


#### Attraction ####
####################

class SmallAttractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attraction
        fields = ['name']


class AttractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attraction
        fields = ['name', 'generalDescription', 'latitude', 'longitude']

# # retrieves minimal information about an attraction, for queries with
# # minimal requirements
# class SmallAttractionSerializer(serializers.ModelSerializer):
#     tag = SmallTagSerializer()

#     class Meta:
#         model = Attraction
#         fields = ['name', 'generalDescription', 'tag']


# # retrieves ALL the information about an attraction
# class LargeAttractionSerializer(serializers.ModelSerializer):
#     images = ImageSerializer(many=True)
#     tag = SmallTagSerializer()
#     ratings = SmallRatingFlagSerializer(source='filtered_ratings', many=True)

#     class Meta:
#         model = Attraction
#         fields = ['name', 'generalDescription', 'latitude', 'longitude', 'images', 'tag', 'ratings']


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['status']


#### Tag ####
#############
        
# will be nested in Attraction Serializers 
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['tagName']

# # with SmallAttractionSerializer nested   
# class LargeTagSerializer(serializers.ModelSerializer):
#     attractions = SmallAttractionSerializer(many=True, read_only=True)
#     class Meta:
#         model = Tag
#         fields = ['tagName','attractions']


#### IsTagged ####
##################

class IsTaggedSerializer(serializers.ModelSerializer):
    class Meta:
        model = IsTagged
        fields = ['tag', 'attraction']


##### Notebook #####
#####################

# used for the list action
class ListNotebookSerializer(serializers.ModelSerializer):
    status = StatusSerializer(read_only=True)
    route = SmallRouteSerializer(read_only=True)

    class Meta:
        model = Notebook
        fields = ['title', 'status', 'route']


# # shows everything it is to know about a specific notebook-entry
# class LargeNotebookSerializer(serializers.ModelSerializer):

#     # route = SmallRouteSerializer() # add route in fields field:) there is an error in smallrouteserializer
#     user = SmallMemberSerializer(read_only=True)
#     status = StatusSerializer(read_only=True)

#     class Meta:
#         model = Notebook
#         fields = ['title', 'note', 'dateStarted', 'status', 'dateCompleted', 'user']


class NotebookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notebook
        fields = ['route', 'title', 'note', 'status', 'dateStarted', 'dateCompleted']
        extra_kwargs = {'dateStarted': {'read_only': True}, 'dateCompleted': {'read_only': True}}

    def create(self, validated_data):
        request = self.context.get('request')

        if not request:
            raise serializers.ValidationError({'request': 'Request related error'})

        member = Member.objects.get(baseUser=request.user)
        # the user making the request gets associated with the current notebook-entry
        validated_data['user'] = member

        # if the user sets the status as 'Completed' upon creation
        if validated_data['status'].status == "Completed":
            # then the Completed date also becomes today's date
            validated_data['dateCompleted'] = date.today()

        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context.get('request')

        if not request: 
            raise serializers.ValidationError({'request': 'Request related error'})

        member = Member.objects.get(baseUser=request.user)
        validated_data['user'] = member
        
        # the previous status
        old_status = instance.status.status

        # the completion date is updated only when the status is set to 'completed' from a previous state
        if validated_data['status'].status == 'Completed' and old_status != 'Completed':
            validated_data['dateCompleted'] = date.today()
        
        # if upon completing the route, the user decides to move it to a previous state, both dates get reset
        elif validated_data['status'].status != 'Completed' and old_status == 'Completed':
            validated_data['dateStarted'] = date.today()
            validated_data['dateCompleted'] = None

        return super().update(instance, validated_data)


#### RatingFlag ####
####################

# # small flag serializer, gives minimal information about rating
# class SmallRatingFlagSerializer(serializers.ModelSerializer):

#     route = ExtraSmallRouteSerializer(read_only=True)
#     attraction = SmallAtractionSerializer(read_only=True)

#     class Meta:
#         model = Rating
#         fields = ['rating', 'comment', 'route', 'attraction']


class RatingFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatingFlag
        fields = ['user', 'rating', 'comment', 'route', 'attraction']
              
    def validate(self, data):
        route = data.get('route')
        attraction = data.get('attraction')
        
        # only one and exactly one of the two nullable fields (route, attraction) can be null at a time
        if route is not None and attraction is not None:
            raise serializers.ValidationError("Only one of route or attraction can be specified.")
        elif route is None and attraction is None:
            raise serializers.ValidationError("Either route or attraction must be specified.")
        
        return data

    def create(self, validated_data):
        request = self.context.get('request')

        if not request:
            raise serializers.ValidationError({'request': 'Request related error'})

        member = Member.objects.get(baseUser=request.user)
        # the user making the request gets associated with the current RatingFlag
        validated_data['user'] = member

        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context.get('request')

        if not request: 
            raise serializers.ValidationError({'request': 'Request related error'})

        member = Member.objects.get(baseUser=request.user)
        # the user making the request gets associated with the current RatingFlag
        validated_data['user'] = member
        
        return super().update(instance, validated_data)


# # large flag serializer, gives detailed information about rating
# class LargeRatingFlagSerializer(serializers.ModelSerializer):

#     user = SmallUserSerializer(read_only=True)
#     route = ExtraSmallRouteSerializer(read_only=True)
#     attraction = SmallAtractionSerializer(read_only=True)

#     class Meta:
#         model = Rating
#         fields = ['user', 'rating', 'comment', 'route', 'attraction']


#### RatingFlagType ####
########################

class RatingFlagTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatingFlagType
        fields = ['type']
        extra_kwargs = {'type': {'read_only': True}}
