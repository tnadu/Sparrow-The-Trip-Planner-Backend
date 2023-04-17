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
  
        
class Tag(models.Model):
    tagName = models.CharField(max_length=100, db_column='tag_name')

    class Meta:
        db_table = 'tag'
        ordering = ['tagName']
        default_related_name = 'tag'


# many - many between Tag & Attraction
class IsTagged(models.Model):
    attraction = models.ForeignKey('Attraction', on_delete=models.CASCADE, db_column='attraction_id')
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE, db_column='tag_id')

    class Meta:
        db_table = 'isTagged'
        unique_together = ('attraction', 'tag')
        default_related_name = 'isTagged'
        #orders the isTagged objects by the id of the Attraction, in reverse order of the id of the isTagged model itself
        #so that the most recent tag for each Attraction appears first.
        ordering = ['attraction', '-id']
  

# a rating can be associated with either a route or an attraction or both, 
# but it is not mandatory to have either of them => the default value of 0 will be stored in the database    
class Rating(models.Model):
    RATING_CHOICES = (
        (0, 'Not rated'),
        (1, 'One star'),
        (2, 'Two stars'),
        (3, 'Three stars'),
        (4, 'Four stars'),
        (5, 'Five stars'),
        (-1, 'Flag'),
    )

    user = models.ForeignKey('Member', on_delete=models.CASCADE, db_column='user_id')
    rating = models.IntegerField(choices=RATING_CHOICES, default=0, db_column='rating')
    comment = models.TextField(null = True, blank = True, db_column='comment')
    route = models.ForeignKey('Route', null=True, blank=True, on_delete=models.CASCADE, db_column='route_id') # nullable
    attraction = models.ForeignKey('Attraction', null=True, blank=True, on_delete=models.CASCADE, db_column='attraction_id') # nullable
    
    class Meta:
        db_table = 'rating'
        unique_together = ('user', 'route', 'attraction')
        default_related_name = 'rating'
