from django.db import models
from apps.organizations.models import Organization


class Customer(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="customers")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    company = models.CharField(max_length=150, blank=True)
    avatar_url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["organization", "email"]),
            models.Index(fields=["organization", "phone"]),
        ]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return self.full_name


class CustomerTag(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="customer_tags")
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=20, default="violet")
    customers = models.ManyToManyField(Customer, related_name="tags", blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["organization", "name"], name="unique_customer_tag")
        ]
