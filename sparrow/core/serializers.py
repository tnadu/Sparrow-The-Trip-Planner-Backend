from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.core.files.storage import default_storage
from django.conf import settings
from .models import *
from datetime import date
import uuid


# includes the email field and is, therefore, accessible
# only to users making requests on their own instance
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


# accessible to all authenticated users
class PrivateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


# nested in the corresponding member serializer and used within related list serializers
class SmallUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class RegisterUserSerializer(serializers.ModelSerializer):
    # field used for a double check of the provided password
    passwordCheck = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'passwordCheck', 'first_name', 'last_name', 'email']
        # the password hashes should not be viewed, nor returned after creation
        extra_kwargs = {'passwordCheck': {'write_only': True}, 'password': {'write_only': True}}

    # custom save method logic, to accommodate password 
    # matching and properly setting the validated password
    def save(self, **kwargs):
        password = self.validated_data['password']
        passwordCheck = self.validated_data['passwordCheck']

        # the two password fields must match
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
# any other default behaviour of a ModelSerializer pollutes the POST request
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
        extra_kwargs = {'password': {'write_only': True}}

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
        else:
            member = Member(
                baseUser=baseUser,
                birthDate=self.validated_data['birthDate']
            )

        member.save()
        return member


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


# nested in related models and used for the list action
class SmallAndListMemberSerializer(serializers.ModelSerializer):
    baseUser = SmallUserSerializer(read_only=True)

    class Meta:
        model = Member
        fields = ['baseUser', 'profilePhoto']


class SmallGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name', 'description']


class BelongsToSerializer(serializers.ModelSerializer):
    class Meta:
        model = BelongsTo
        fields = ['id', 'user', 'group', 'isAdmin', 'nickname']


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ['id', 'title', 'description', 'verified', 'public', 'startingPointLat', 'startingPointLon', 'publicationDate', 'user', 'group']
        extra_kwargs = {'verified': {'read_only': True}, 'publicationDate': {'read_only': True}}

    # only one and exactly one of the two nullable fields (group, user) can be null at a time.
    def validate(self, data):
        group = data.get('group')
        user = data.get('user')

        if (user is not None and group is not None) or (user is None and group is None):
            raise serializers.ValidationError("Only one of user and group can be specified")
        
        # making sure that unspecified fields are set to None, instead of outright not existing
        data['group'] = group
        data['user'] = user

        return data


# retrieves partial information about a route
class ListRouteSerializer(serializers.ModelSerializer):
    user = SmallAndListMemberSerializer()
    group = SmallGroupSerializer()

    class Meta:
        model = Route
        fields = ['id', 'title', 'description', 'verified', 'startingPointLat', 'startingPointLon', 'publicationDate', 'user', 'group']
        extra_kwargs = {'publicationDate': {'read_only': True}}


class SmallRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ['id', 'title']


class IsWithinSerializer(serializers.ModelSerializer):
    class Meta:
        model = isWithin
        fields = ['id', 'route', 'attraction', 'orderNumber']


class SmallAttractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attraction
        fields = ['id', 'name']


class AttractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attraction
        fields = ['id', 'name', 'generalDescription', 'latitude', 'longitude']


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['id', 'status']

        
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'tagName']


class IsTaggedSerializer(serializers.ModelSerializer):
    class Meta:
        model = IsTagged
        fields = ['id', 'tag', 'attraction']


class ListNotebookSerializer(serializers.ModelSerializer):
    status = StatusSerializer(read_only=True)
    route = SmallRouteSerializer(read_only=True)

    class Meta:
        model = Notebook
        fields = ['id', 'title', 'status', 'route']


# this serializer is designed to handle image objects, 
# including saving newly uploaded images both in the 
# db and on disk, and also deleting images when needed
class ImageUploadSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(write_only=True)

    # the class constructor of this serializer stores the values of folder_name, notebook, attraction, 
    # and owner attributes for each image that is being created
    # these values are used later during the image creation process
    def __init__(self, folder_name=None, notebook=None, attraction=None, owner=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.folder_name = folder_name
        self.notebook = notebook
        self.attraction = attraction
        self.owner = owner

    class Meta:
        model = Image
        fields = ['id', 'image', 'imagePath']
        read_only_fields=['imagePath']

    def create(self, validated_data):
        image = validated_data.pop('image')

        # I am retrieving the extension of the file and generating a unique file name for the current file
        file_extension = image.name.split('.')[-1]
        generated_unique_filename = '{}.{}'.format(uuid.uuid4(), file_extension)

        # the file_path variable is set to the merging of the destination folder_name 
        # and the newly generated unique filename for the current file
        self.file_path =  self.folder_name + generated_unique_filename

        validated_data['imagePath'] = self.file_path
        validated_data['notebook'] = self.notebook
        validated_data['attraction'] = self.attraction
        validated_data['owner'] = self.owner

        # save the uploaded image file to the media directory
        # I am uploading the files using chunks of data as this action can consume a lot of server resources, 
        # so this aproach can help reduce memory usage and improve performance
        # 'wb+' => reading and writting a file in binary
        with default_storage.open(settings.MEDIA_ROOT + '/' + self.file_path, 'wb+') as destination:
            for chunk in image.chunks():
                destination.write(chunk)

        instance = super().create(validated_data)
        instance.save()
        return instance
    
    # the delete method of the serializer is responsible for removing instances 
    # from both the database and the corresponding folder where the image file is stored
    def delete(self, instance):
        try:
            default_storage.delete(instance.imagePath)
        except Exception as e:
            raise ValidationError('Failed to delete image {}'.format(instance.imagePath))

        instance.delete()


class NotebookSerializer(serializers.ModelSerializer):
    images = serializers.ListField(required=False)
    images_list = serializers.SerializerMethodField()

    class Meta:
        model = Notebook
        fields = ['id', 'route', 'title', 'note', 'status', 'dateStarted', 'dateCompleted', 'images', 'images_list']
        extra_kwargs = {'dateStarted': {'read_only': True}, 'dateCompleted': {'read_only': True}}

    # this method retrieves and returns a list of all the images 
    # associated with the current instance of the Notebook class
    def get_images_list(self, obj):
        images = Image.objects.filter(notebook=obj)
        return [image.imagePath for image in images]

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

        # the serializer is iterating through the images and assigning 
        # them to the current notebook and owner before saving them to the database
        # I am using ImageUploadSerializer
        images_data = validated_data.pop('images', [])
        notebook = Notebook.objects.create(**validated_data)
        images = []

        for image_data in images_data:
            image_serializer = ImageUploadSerializer(folder_name='notebook_images/', notebook=notebook, owner = member, data={'image': image_data})
            if image_serializer.is_valid(raise_exception=True):
                image = image_serializer.save()
                images.append(image)

        return notebook
    

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

        # appending new images to the existing list
        # the serializer is iterating through the images and assigning 
        # them to the current notebook and owner before saving them to the database
        # I am using ImageUploadSerializer
        images_data = validated_data.pop('images', [])

        for image_data in images_data:
            image_serializer = ImageUploadSerializer(folder_name='notebook_images/', notebook=instance, owner=member, data={'image': image_data})
            if image_serializer.is_valid(raise_exception=True):
                image = image_serializer.save()

        return super().update(instance, validated_data)


class RatingFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatingFlag
        fields = ['id', 'user', 'rating', 'comment', 'route', 'attraction']
        read_only_fields = ['user']
        
    def validate(self, data):
        route = data.get('route')
        attraction = data.get('attraction')
        
        # only one and exactly one of the two nullable fields (route, attraction) can be null at a time
        if (route is not None and attraction is not None) or (route is None and attraction is None):
            raise serializers.ValidationError("Either 'route' or 'attraction' must be specified.")

        # making sure that unspecified fields are set to None, instead of outright not existing
        data['route'] = route
        data['attraction'] = attraction

        return data
    
    def save(self, **kwargs):
        assert hasattr(self, '_errors'), (
            'You must call `.is_valid()` before calling `.save()`.'
        )

        assert not self.errors, (
            'You cannot call `.save()` on a serializer with invalid data.'
        )

        # Guard against incorrect use of `serializer.save(commit=False)`
        assert 'commit' not in kwargs, (
            "'commit' is not a valid keyword argument to the 'save()' method. "
            "If you need to access data before committing to the database then "
            "inspect 'serializer.validated_data' instead. "
            "You can also pass additional keyword arguments to 'save()' if you "
            "need to set extra attributes on the saved model instance. "
            "For example: 'serializer.save(owner=request.user)'.'"
        )

        assert not hasattr(self, '_data'), (
            "You cannot call `.save()` after accessing `serializer.data`."
            "If you need to access data before committing to the database then "
            "inspect 'serializer.validated_data' instead. "
        )

        validated_data = {**self.validated_data, **kwargs}

        currentUser = self.context['request'].user
        validated_data['user'] = Member.objects.get(baseUser=currentUser)

        if self.instance is not None:
            self.instance = self.update(self.instance, validated_data)
            assert self.instance is not None, (
                '`update()` did not return an object instance.'
            )
        else:
            self.instance = self.create(validated_data)
            assert self.instance is not None, (
                '`create()` did not return an object instance.'
            )

        return self.instance


class RatingFlagTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatingFlagType
        fields = ['id', 'type']
        extra_kwargs = {'type': {'read_only': True}}
