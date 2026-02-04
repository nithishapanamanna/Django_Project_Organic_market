from django.conf import settings
from django.db import models

class FarmerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='farmer_profile'
    )
    phone = models.CharField(max_length=15)
    location = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='farmers/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
