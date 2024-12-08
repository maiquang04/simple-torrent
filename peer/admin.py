from django.contrib import admin
from .models import UserProfile


# Register your models here.
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "peer_id", "default_directory")
    search_fields = ("user__username", "peer_id")
    list_filter = ("default_directory",)
