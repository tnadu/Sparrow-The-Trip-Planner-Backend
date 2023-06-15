from django.contrib import admin
from .models import *


# Register your models here.
admin.site.register(Route)
admin.site.register(isWithin)
admin.site.register(Attraction)
                    
admin.site.register(Member)
admin.site.register(Group)
admin.site.register(BelongsTo)
admin.site.register(Status)
admin.site.register(Notebook)
admin.site.register(Tag)
admin.site.register(RatingFlagType)
admin.site.register(IsTagged)
admin.site.register(RatingFlag)
admin.site.register(Image)
