from rest_framework import serializers, filters
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from .models import *
from datetime import date
from django.core.files.storage import default_storage
from django.conf import settings
import uuid

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


#### Group #####
################
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

# class LargeGroupSerializer(serializers.ModelSerializer):
#     members = MemberBelongsToSerializer(many=True, read_only=True)
#     routes = ExtraSmallRouteSerializer(many=True, read_only=True)

#     class Meta:
#         model = Group
#         fields = ['name', 'description', 'members', 'routes']

##### BelongsTo #####
#####################

# class WriteBelongsToSerializer(serializers.ModelSerializer):
#     member = serializers.PrimaryKeyRelatedField()
#     group = serializers.PrimaryKeyRelatedField()

#     class Meta:
#         model = BelongsTo
#         fields = ['member', 'group', 'isAdmin', 'nickname']


class GroupBelongsToSerializer(serializers.ModelSerializer):
    groups = SmallGroupSerializer(many=True, read_only=True)

    class Meta:
        model = BelongsTo
        fields = ['groups', 'isAdmin', 'nickname']


class MemberBelongsToSerializer(serializers.ModelSerializer):
    members = SmallMemberSerializer(many=True, read_only=True)
    
    class Meta:
        model = BelongsTo
        fields = ['members', 'isAdmin', 'nickname']


##### Route #####
#####################
# used for write operations (post/put)
class WriteRouteSerializer(serializers.ModelSerializer):
    # i already have the field defined in the model
    # user = serializers.PrimaryKeyRelatedField(read_only=True)
    # group = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Route
        fields = ['title', 'description', 'verified', 'public', 'startingPointLat', 'startingPointLon', 'user', 'group']

    # Only one and exactly one of the two nullable fields (group, user) can be null at a time.
    def validate(self, data):
        user = data.get('user')
        group = data.get('group')
        if (user is not None and group is not None) or (user is None and group is None):
            raise serializers.ValidationError("Only one of user and group can be specified")
        return data


# retreives ALL the information for a a route
# class LargeRouteSerializer(serializers.ModelSerializer):
#     author = SmallMemberSerializer()
#     is_within = IsWithinSerializer(many=True)  # one for each attraction of the route
#     group = SmallGroupSerializer()

#     class Meta:
#         model = Route
#         fields = ['title', 'description', 'verified', 'public', 'startingPointLat', 'startingPointLon',
#                   'publicationDate',
#                   'author', 'is_within', 'group']


# retrieves partial information about a route
class SmallRouteSerializer(serializers.ModelSerializer):
    author = SmallMemberSerializer()
    group = SmallGroupSerializer()

    class Meta:
        model = Route
        fields = ['title', 'description', 'verified', 'author', 'group']


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


# retrieves minimal information about an attraction, for queries with
# minimal requirements
# class SmallAttractionSerializer(serializers.ModelSerializer):
#     tag = SmallTagSerializer()

#     class Meta:
#         model = Attraction
#         fields = ['name', 'generalDescription', 'tag']

# retrieves ALL the information about an attraction
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

#used for write operations (post/put)
class WriteRatingFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatingFlag
        fields = ['user', 'rating', 'comment', 'route', 'attraction']
              
    def validate(self, data):
        route = data.get('route')
        attraction = data.get('attraction')
        
        #only one and exactly one of the two nullable fields (route, attraction) can be null at a time
        if route is not None and attraction is not None:
            raise serializers.ValidationError("Only one of route or attraction can be specified.")
        elif route is None and attraction is None:
            raise serializers.ValidationError("Either route or attraction must be specified.")
        
        return data
        


# will be nested in Attraction Serializers 
class SmallTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['tagName']

# with SmallAttractionSerializer nested   
# class LargeTagSerializer(serializers.ModelSerializer):
#     attractions = SmallAttractionSerializer(many=True, read_only=True)
#     class Meta:
#         model = Tag
#         fields = ['tagName','attractions']


#used for write operations (post/put)      
class WriteIsTaggedSerializer(serializers.ModelSerializer):
    class Meta:
        model = IsTagged
        fields = ['tag', 'attraction']


##### Notebook #####
#####################

# notebook serializers
# shows minimum of information, used when displaying all entries in a list
class SmallNotebookSerializer(serializers.ModelSerializer):

    status = StatusSerializer(read_only=True)
    class Meta:
        model = Notebook
        fields = ['title', 'note', 'status']

# shows everything it is to know about a specific notebook-entry
class LargeNotebookSerializer(serializers.ModelSerializer):

    # route = SmallRouteSerializer() # add route in fields field:) there is an error in smallrouteserializer
    user = SmallMemberSerializer(read_only=True)
    status = StatusSerializer(read_only=True)

    class Meta:
        model = Notebook
        fields = ['title', 'note', 'dateStarted', 'status', 'dateCompleted', 'user']

# used to display only the fields necessary when put / post requests are made
class WriteNotebookSerializer(serializers.ModelSerializer):
    
    # using a custom create function as I need to make a few modifications
    # before saving the object in the database
    def create(self, validated_data):
        request = self.context.get('request')

        # if the user making the request is authenticated
        if request:

            member = Member.objects.get(baseUser=request.user)
            # they become the user of the current notebook-entry, note that the member object was added
            validated_data['user'] = member
            # the starting date of the current entry becomes today's date
            validated_data['dateStarted'] = date.today()

            # if the user sets the status as 'Completed' upon creation
            if validated_data['status'].status == "Completed":
                # then the Completed date also becomes today's date
                validated_data['dateCompleted'] = date.today()
        else:
            raise serializers.ValidationError({'request': 'Request related error'})
        
        # if there are no modifications made regarding: dateCompleted -> it remains null 
        # calling parent class function to perform better validation of data
        return super().create(validated_data)

    # same goes for update
    def update(self, instance, validated_data):
        request = self.context.get('request')

        if request:
            member = Member.objects.get(baseUser=request.user)
            validated_data['user'] = member
            # the previous status
            old_status = instance.status.status

            # the user wants to change the status of the trip
            # it changes it from anything (including 'Completed') to 'Completed'
            if validated_data['status'].status == 'Completed':
                # then the completion date also changes
                validated_data['dateCompleted'] = date.today()
            
            # it changes it from 'Completed' to anything (including 'Completed')
            elif old_status == 'Completed':
                # the completion date becomes null
                validated_data['dateCompleted'] = None
                # the starting date is also modified
                validated_data['dateStarted'] = date.today()
        else:
            raise serializers.ValidationError({'request': 'Request related error'})
        # calling parent class function to perform better validation of data
        return super().update(instance, validated_data)
    
    class Meta:
        model = Notebook
        fields = ['route', 'title', 'note', 'status']

# small flag serializer, gives minimal information about rating
# class SmallRatingFlagSerializer(serializers.ModelSerializer):

#     route = ExtraSmallRouteSerializer(read_only=True)
#     attraction = SmallAtractionSerializer(read_only=True)

#     class Meta:
#         model = Rating
#         fields = ['rating', 'comment', 'route', 'attraction']

# large flag serializer, gives detailed information about rating
# class LargeRatingFlagSerializer(serializers.ModelSerializer):

#     user = SmallUserSerializer(read_only=True)
#     route = ExtraSmallRouteSerializer(read_only=True)
#     attraction = SmallAtractionSerializer(read_only=True)

#     class Meta:
#         model = Rating
#         fields = ['user', 'rating', 'comment', 'route', 'attraction']

class ImageUploadSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(write_only = True)

    class Meta:
        model = Image
        fields = ['image', 'imagePath']
        read_only_fields = ['imagePath']

    def create(self, validated_data, folder_name = 'miscellaneous/'):
        image = validated_data.pop('image')
        instance = super().create(validated_data)

        file_extension = image.name.split('.')[-1]
        generated_unique_filename = '{}.{}'.format(uuid.uuid4(), file_extension)
        instance.imagePath = generated_unique_filename

        # save the uploaded image file to the media directory
        # I am uploading the files using chunks of data as this action can consume a lot of server resources, 
        # so this aproach can help reduce memory usage and improve performance
        # 'wb+' => reading and writting a file in binary
        file_path =  folder_name + generated_unique_filename
        with default_storage.open(settings.MEDIA_ROOT + '/' + file_path, 'wb+') as destination:
            for chunk in image.chunks():
                destination.write(chunk)
        return instance
    
class NotebookImageUpload(serializers.ModelSerializer):
    image = ImageUploadSerializer(write_only = True)
    notebook = serializers.PrimaryKeyRelatedField(queryset=Notebook.objects.all())

    class Meta:
        model = Image
        fields = ['image', 'imagePath', 'notebook']
        read_only_fields = ['imagePath']

    def create(self, validated_data):
        image_serializer = self.fields['image']
        folder_name = 'notebook_images/'

        image = image_serializer.create(validated_data=validated_data.pop('image'), folder_name=folder_name)
        validated_data['notebook'] = self.validated_data['notebook']
        validated_data['imagePath'] = image.imagePath

        instance = super().create(validated_data)
        instance.save()
        return instance
