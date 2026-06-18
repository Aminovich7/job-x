from django.contrib import admin

from .models import Bid, Project


admin.site.register(Project)
admin.site.register(Bid)
