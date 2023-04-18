from django.db import models
from django.contrib.auth.models import User


# many - many between Route & Attraction
class isWithin (models.Model):
    route = models.ForeignKey('Route', on_delete=models.CASCADE, db_column='route_id')
    attraction = models.ForeignKey('Attraction', on_delete=models.CASCADE, db_column='attraction_id')
    # the orderNumber of the attraction in the current route
    orderNumber = models.IntegerField(db_column='order_number') 
    
    class Meta:
        db_table = 'isWithin'
        unique_together = ('route', 'attraction')
        default_related_name = 'isWithin'


class Route(models.Model):
    title = models.CharField(max_length=50, db_column='title')
    description = models.CharField(max_length=3000, db_column='description')
    verified = models.BooleanField(default=False, db_column='verified')
    public = models.BooleanField(default=False, db_column='public')
    startingPointLat = models.FloatField(db_column='starting_point_lat')
    startingPointLon = models.FloatField(db_column='starting_point_lon')
    publicationDate = models.DateTimeField('date published', auto_now_add=True, db_column='routePublicationDate')
    user = models.ForeignKey('Member', on_delete=models.CASCADE, null=True, blank=True, db_column='route_user')  # nullable
    group = models.ForeignKey('Group', on_delete=models.CASCADE, null=True, blank=True, db_column='route_group')  # nullable
    
    class Meta:
        db_table = 'route'
        ordering = ['publicationDate', 'user']
        default_related_name = 'route'

    def __str__(self):
        return self.title + self.description

class Attraction(models.Model):
    name = models.CharField(max_length=100, db_column='name')
    generalDescription = models.CharField(max_length=3000, db_column='general_description')
    photo = models.ImageField(upload_to='attraction_photos', default='attraction_photo_default.jpg', db_column='photo')
    latitude = models.FloatField(db_column='latitude')
    longitude = models.FloatField(db_column='longitude')

    class Meta:
        db_table = 'attraction'
        ordering = ['name']
        default_related_name = 'attraction'

# member model, extending the User model via a one-to-one relationship;
# a member instance is generated whenever a user signs up, with both 
# 'profilePhoto' and 'birthDate' fields set to null; 
# these values can be set when updating the profile of a user;
class Member(models.Model):
    baseUser = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    profilePhoto = models.ImageField(upload_to='profile-photos', default='default-profile-photo.jpeg', db_column='profile_photo')
    birthDate = models.DateField(null=True, db_column='birth_date')

    class Meta:
        db_table = 'member'
        ordering = ['baseUser']
        default_related_name = 'member'


class Group(models.Model):
    name = models.CharField(max_length=30, db_column='name')
    description = models.CharField(max_length=1500, db_column='description')
    
    class Meta:
        db_table = 'group'
        default_related_name = 'group'


# associative table between 'Member' and 'Group'
class BelongsTo(models.Model):
    member = models.ForeignKey('Member', on_delete=models.CASCADE, db_column='member_id')
    group = models.ForeignKey('Group', on_delete=models.CASCADE, db_column="group_id")
    isAdmin = models.BooleanField(db_column="isAdmin")
    nickname = models.CharField(max_length=50, null=True, blank=True, db_column="nickname")

    class Meta:
        db_table = 'belongsTo'
        default_related_name = 'belongsTo'
        # cannot have multiple identical entries for belonging relationship
        unique_together = ('member', 'group')
