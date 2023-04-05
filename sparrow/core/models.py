import datetime

from django.db import models
from django.utils import timezone
from django.contrib import admin
from datetime import datetime
#from django.contrib.auth.models import User, Group

class Route(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    verified = models.BooleanField(default=False)
    public = models.BooleanField(default=False)
    startingPointLat = models.FloatField()
    startingPointLon = models.FloatField()
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    user = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True) # nullable, when the user is deleted the route isnt
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True) #nullable
    class Meta:
        ordering = ['pub_date', 'user']

    def change_starting_point(self, new_lat, new_lon):
        self.startingPointLat = new_lat
        self.startingPointLon = new_lon
        self.save()

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
        ordering = ['user']
        db_table = 'member'
        default_related_name = 'member'

