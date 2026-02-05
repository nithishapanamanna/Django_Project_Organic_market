from django.conf import settings
from django.db import models
from farmer.models import FarmerProfile

class Product(models.Model):
    CATEGORY = (
        ('fruit', 'Fresh Fruits'),
        ('vegetable', 'Daily Vegetables'),
        ('dairy', 'Dairy Products'),
        ('Batter', 'Batter,Breads & Chapati'),
        ('spices', 'Spices & Herbs'),
        ('beverages', 'Beverages'),
        ('snacks', 'Snacks & Sweets'),
        ('others', 'Others'),
    )
    farmer = models.ForeignKey(
        FarmerProfile,
        on_delete=models.CASCADE,
        related_name='products'
    )
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    harvest_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to='products/',null=True,blank=True)
    is_approved = models.BooleanField(default=False)
    rejection_reason = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} - {self.rating}"
