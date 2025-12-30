from django.db import models
from django.contrib.auth.models import User
from store.models import Product

class Order(models.Model):
    STATUS_CHOICES = (('Pending','Pending'),('Confirmed','Confirmed'),('Dispatch','Dispatch'),('Delivered','Delivered'),('Return','Return'),('Cancel','Cancel'))
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=50); last_name = models.CharField(max_length=50)
    email = models.EmailField(); phone = models.CharField(max_length=20)
    address = models.TextField(); city = models.CharField(max_length=50)
    payment_method = models.CharField(max_length=20, default='cod')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    def __str__(self): return f"Order {self.id}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)