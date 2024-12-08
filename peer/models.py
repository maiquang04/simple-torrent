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

    def set_peer_id(self):
        self.peer_id = f"{self.user.username}-{uuid.uuid4().hex}"

    def save(self, *args, **kwargs):
        if not self.peer_id:
            self.set_peer_id()
        super(UserProfile, self).save(*args, **kwargs)
