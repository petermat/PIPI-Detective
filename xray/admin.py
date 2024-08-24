from django.contrib import admin

# Register your models here.
from .models import Snapshot

# Define the admin class

@admin.register(Snapshot)
class SnapshotAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Snapshot._meta.get_fields()]