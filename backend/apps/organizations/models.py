from django.conf import settings
from django.db import models


class Organization(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=180, unique=True)
    logo_url = models.URLField(blank=True)
    timezone = models.CharField(max_length=64, default="Asia/Kathmandu")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="Membership",
        related_name="organizations",
    )

    def __str__(self):
        return self.name


class Membership(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=20, choices=[
        ("owner", "Owner"),
        ("admin", "Admin"),
        ("manager", "Manager"),
        ("agent", "Agent"),
    ], default="agent")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["organization", "user"], name="unique_org_member")
        ]
