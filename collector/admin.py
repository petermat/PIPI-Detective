from django.contrib import admin

# Register your models here.
from .models import Pipipackage

# Define the admin class

@admin.register(Pipipackage)
class PipipackageAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Pipipackage._meta.get_fields()]