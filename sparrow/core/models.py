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


# notebook model, used to store information about a user's experience with a particular route
# this information includes their impressions, notes, and any photos they took during the trip
# additionally, the model records the date and time of the journey;
# 'route' - foreignKey, it specifies the route associated with the current entry in the notebook;
# 'user' - foreignKey, holds the user who created the notebook;
# 'status' - foreignKey, it specifies the current status of the trip
class Notebook(models.Model):
    route = models.ForeignKey('Route', null=False, blank=False, on_delete=models.CASCADE, db_column='route_id')
    user = models.ForeignKey('Member', null=False, blank=False, on_delete=models.CASCADE, db_column='user_id')

    # added a choices attribute to the Status model for easier access through a dropdown menu, 
    # enabling me to select from pre-defined options and validate data
    status = models.ForeignKey('Status', choices=models.Status.get_choices(), on_delete=models.CASCADE, null = True, blank = True, db_column='status_id')
    
    # added a title for the current notebook entry
    title = models.CharField(null = True, blank=True, db_column='title')
    note = models.TextField(null = True, blank = True, db_column = 'note')
    # default max-length value for image field is 100 characters
    photo = models.ImageField(upload_to='notebook-photos', null = True, blank = True, db_column='photo')
    dateStarted = models.DateField(null = True, db_column = 'dateStarted') # nullable
    dateCompleted = models.DateField(null = True, db_column = 'dateCompleted') # nullable

    class Meta:
        db_table = 'notebook'
        ordering = ['dateStarted', 'dateCompleted', 'title']
        default_related_name = 'notebook'
        
    def __str__(self):
        return self.title

# status model, used to store information about the state of a journey, 
# such as whether it is completed, finished, ongoing, etc.
class Status(models.Model):
    status = models.CharField(null = False, blank = False, db_column='status')

    # get_choices extracts existing statuses from the database and returns a list of tuples (id, status_title)
    # this is useful for defining the choices field of any notebook entry that requires a status value, 
    # ensuring that the options are up-to-date and consistent with the database values.
    @classmethod
    def get_choices(cls):
        return [(status.id, status.status) for status in cls.objects.all()]

    class Meta:
        db_table = 'status'
        ordering = ['status']
        default_related_name = 'status'
    
    def __str__(self):
        return self.status