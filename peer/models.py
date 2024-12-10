from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


# Create your models here.
class User(AbstractUser):
    pass


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    default_directory = models.CharField(max_length=255, blank=True, null=True)
    peer_id = models.CharField(
        max_length=255, unique=True, blank=True, null=True
    )
    is_active = models.BooleanField(default=True)  # Track user's active status

    def set_peer_id(self):
        self.peer_id = f"{self.user.username}-{uuid.uuid4().hex}"

    def save(self, *args, **kwargs):
        if not self.peer_id:
            self.set_peer_id()
        super(UserProfile, self).save(*args, **kwargs)

        # Upate UserTorrent objects if is_active is False
        if not self.is_active:
            self.usertorrent_set.update(is_available=False)


class Torrent(models.Model):
    name = models.CharField(max_length=255)  # File name
    file_length = models.BigIntegerField()  # Total file length in bytes
    piece_length = models.IntegerField()  # Piece length in bytes
    info_hash = models.CharField(
        max_length=40
    )  # SHA-1 hash of the 'info' dictionary
    created_at = models.DateTimeField(
        auto_now_add=True
    )  # Timestamp of creation
    uploaded_by = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="torrents"
    )

    @property
    def seeders(self):
        # Count UserTorrent objects with is_available=True for this torrent
        return self.usertorrent_set.filter(is_available=True).count()

    @property
    def leechers(self):
        # Count UserTorrent objects with is_available=False for this torrent
        return self.usertorrent_set.filter(is_available=False).count()

    def __str__(self):
        return f"{self.name} ({self.file_length} bytes)"


class Piece(models.Model):
    torrent = models.ForeignKey(
        Torrent, on_delete=models.CASCADE, related_name="pieces"
    )
    index = models.IntegerField()  # Piece index
    hash_value = models.CharField(max_length=40)  # SHA-1 hash of the piece

    def __str__(self):
        return f"Piece {self.index} of Torrent {self.torrent.name}"


class UserTorrent(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    torrent = models.ForeignKey(Torrent, on_delete=models.CASCADE)
    current_directory = models.CharField(max_length=255)
    file_path = models.CharField(max_length=255)
    is_available = models.BooleanField(
        default=True
    )  # Track if the file is available in the peer directory

    def __str__(self):
        return f"{self.user.user.username} - {self.torrent.name}"
