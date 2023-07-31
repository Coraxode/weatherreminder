from django.contrib import admin
from .models import City, UserSubscriptions, Subscription

admin.site.register(UserSubscriptions)
admin.site.register(Subscription)
admin.site.register(City)
