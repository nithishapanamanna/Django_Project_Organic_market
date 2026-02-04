from django.conf import settings
from django.db import models



class CustomerProfile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    is_verified = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username
