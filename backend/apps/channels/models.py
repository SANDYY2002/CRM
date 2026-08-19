from django.db import models
from apps.organizations.models import Organization


class Channel(models.Model):
    class Types(models.TextChoices):
        FACEBOOK = "facebook", "Facebook"
        INSTAGRAM = "instagram", "Instagram"
        WHATSAPP = "whatsapp", "WhatsApp"
        VIBER = "viber", "Viber"
        YOUTUBE = "youtube", "YouTube"
        WEBSITE = "website", "Website"
        EMAIL = "email", "Email"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="channels")
    type = models.CharField(max_length=30, choices=Types.choices)
    name = models.CharField(max_length=150)
    external_id = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    credentials = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["organization", "type", "external_id"], name="unique_channel_external_id")
        ]
