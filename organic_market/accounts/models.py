from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from orders.models import Order
User = settings.AUTH_USER_MODEL

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('FARMER', 'Farmer'),
        ('CUSTOMER', 'Customer'),
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES
    )

class Payment(models.Model):
    STATUS_CHOICES = (
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('PENDING', 'Pending'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order_id} - {self.amount}"


