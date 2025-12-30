from django.db import models
from django.contrib.auth.models import User


class Membership(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Member: {self.user.username}"