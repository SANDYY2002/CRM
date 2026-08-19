from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Roles(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Admin"
        MANAGER = "manager", "Manager"
        AGENT = "agent", "Agent"

    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.AGENT)
    avatar_url = models.URLField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    is_online = models.BooleanField(default=False)

    def __str__(self):
        return self.get_full_name() or self.username
