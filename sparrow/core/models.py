import datetime

from django.db import models
from django.utils import timezone
from django.contrib import admin
from datetime import datetime
#from django.contrib.auth.models import User, Group


# many - many between Route & Attraction
class isWithin (models.Model):
    route = models.ForeignKey('Route', on_delete=models.CASCADE, db_column='isWithinRouteId')
    attraction = models.ForeignKey('Attraction', on_delete=models.CASCADE, db_column='isWithinAttractionId')
    orderNumber = models.IntegerField(db_column='isWithinOrderNumber') # the orderNumber of the attraction in the current route
    class Meta:
        db_table = 'isWithin'
        unique_together = ('route', 'attraction')

class Route(models.Model):
    title = models.CharField(max_length=50, db_column='route_title')
    description = models.CharField(max_length=3000, db_column='route_description')
    verified = models.BooleanField(default=False, db_column='route_verified')
    public = models.BooleanField(default=False, db_column='route_public')
    startingPointLat = models.FloatField(db_column='route_starting_point_lat')
    startingPointLon = models.FloatField(db_column='route_starting_point_lon')
    publicationDate = models.DateTimeField('date published', auto_now_add=True, db_column='routePublicationDate')
    user = models.ForeignKey(Member, on_delete=models.CASCADE, null=True, blank=True, db_column='route_user')  # nullable
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True, db_column='route_group')  # nullable
    class Meta:
        ordering = ['publicationDate', 'user']

    def __str__(self):
        return self.title + self.description

# member model, extending the User model via a one-to-one relationship;
# a member instance is generated whenever a user signs up, with both 
# 'profilePhoto' and 'birthDate' fields set to null; 
# these values can be set when updating the profile of a user;
class Member(models.Model):
    baseUser = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    profilePhoto = models.ImageField(upload_to='profile-photos', default='default-profile-photo.jpeg', db_column='profile_photo')
    birthDate = models.DateField(null=True, db_column='birth_date')

    class Meta:
        ordering = ['baseUser']
        db_table = 'member'
        default_related_name = 'member'


class Group(models.Model):
    name = models.CharField(max_length=30, db_column='name')
    description = models.CharField(max_length=1500, db_column='description')
    
    class Meta:
        db_table = 'group'
        default_related_name = 'group'
