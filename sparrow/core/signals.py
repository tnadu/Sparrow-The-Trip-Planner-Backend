from django.core.management import call_command
from django.db.models.signals import post_save,post_migrate
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Member, Tag, RatingFlag
import os


# signals allow various components to notify other components
# whenever some action is completed;
# whenever 'post_save' (used to save instances to the database)
# is issued on the User model and gets executed successfully,
# the function bellow will be called;
@receiver(post_save, sender=User)
def createMember(sender, instance, created, **kwargs):
    # once the User instance is created, a Member instance based
    # on said User will also be created and saved;
    if created:
        Member.objects.create(baseUser=instance)
        
@receiver(post_migrate)
def defaultValues_for_tag(sender, **kwargs):
    if sender.name == 'core' and Tag.objects.count() == 0:
        fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'initial_tag.json')
        call_command('loaddata', fixture_path)
        
@receiver(post_migrate)
def defaultValues_for_ratingFlag(sender, **kwargs):
    if sender.name == 'core' and RatingFlag.objects.count() == 0:
        fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'initial_ratingFlag.json')
        call_command('loaddata', fixture_path)

