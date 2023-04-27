from django.core.management import call_command
from django.db.models.signals import post_save,post_migrate,pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Member, Status, Tag, RatingFlagType, Notebook, Image
import os
from django.conf import settings
from django.core.exceptions import ValidationError


# whenever 'post_save' (used to save instances to the database)
# is issued on the User model and gets executed successfully,
# the function bellow will be called;
@receiver(post_save, sender=User)
def createMember(sender, instance, created, **kwargs):
    # once the User instance is created, a Member instance based
    # on said User will also be created and saved;
    if created:
        Member.objects.create(baseUser=instance)


# 'post_migrate' (used to commit modifications made to the database structure)
# this function is called whenever the 'post_migrate' signal is triggered by the core app;
# its purpose is to check whether the 'Status' table has been populated with default values
# for the 'status' field, and to fill in any missing values if necessary.
@receiver(post_migrate)
def statusSeed(sender, **kwargs):
    if sender.name == 'core' and Status.objects.count() == 0:
        fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'initial_status.json')
        call_command('loaddata', fixture_path)


@receiver(post_migrate)
def tagSeed(sender, **kwargs):
    if sender.name == 'core' and Tag.objects.count() == 0:
        fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'initial_tag.json')
        call_command('loaddata', fixture_path)
        

@receiver(post_migrate)
def ratingFlagTypeSeed(sender, **kwargs):
    if sender.name == 'core' and RatingFlagType.objects.count() == 0:
        fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'initial_ratingFlagType.json')
        call_command('loaddata', fixture_path)

# this function is responsible for creating sub-directories within the "media" folder
# the sub-directories are created based on the type of images, 
# which could be either related to notebooks or attractions
@receiver(post_migrate)
def create_media_subdirectories(sender, **kwargs):
    if sender.name == 'core':
        images_dir = [os.path.join(settings.MEDIA_ROOT, 'notebook_images'),
                    os.path.join(settings.MEDIA_ROOT, 'attraction_images')]
        for path in images_dir:
            if not os.path.exists(path):
                os.makedirs(path)

# cron job
@receiver(pre_delete, sender=Notebook)
def sweep_notebook_associated_images(sender, instance, **kwargs):
    images = Image.objects.filter(notebook=instance)
    for image in images:
        try:
            os.remove(settings.MEDIA_ROOT + '/' + image.imagePath)
        except OSError:
            raise ValidationError('Failed to delete image {}'.format(image.imagePath))