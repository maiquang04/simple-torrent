from django.contrib import admin
from .models import UserProfile, Torrent, Piece, UserTorrent


# Register your models here.
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "peer_id", "default_directory")
    search_fields = ("user__username", "peer_id")
    list_filter = ("default_directory", "is_active")


@admin.register(Torrent)
class TorrentAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "file_length",
        "piece_length",
        "info_hash",
        "uploaded_by",
        "seeders",
        "leechers",
        "created_at",
    )
    search_fields = ("name", "info_hash", "uploaded_by__user__username")
    list_filter = ("created_at",)


@admin.register(Piece)
class PieceAdmin(admin.ModelAdmin):
    list_display = ("torrent", "index", "hash_value")
    search_fields = ("torrent__name", "hash_value")
    list_filter = ("torrent",)


@admin.register(UserTorrent)
class UserTorrentAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "torrent",
        "current_directory",
        "file_path",
        "is_available",
    )
    search_fields = ("user__user__username", "torrent__name", "peer_id")
    list_filter = ("is_available", "torrent")
