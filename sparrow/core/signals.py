from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Member


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

