from django.contrib import admin

from .models import Repository, Analysis, Tool

admin.site.register(Repository)
admin.site.register(Analysis)
admin.site.register(Tool)