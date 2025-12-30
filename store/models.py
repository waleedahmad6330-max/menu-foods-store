from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    parents = models.ManyToManyField('self', related_name='children', blank=True, symmetrical=False)
    def __str__(self): return self.name
    class Meta: verbose_name_plural = "Categories"

class Product(models.Model):
    categories = models.ManyToManyField(Category, related_name='products')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    ingredients = models.TextField(blank=True, help_text="Enter ingredients here. Press Enter for new lines.")
    how_to_use = models.TextField(blank=True, help_text="Usage instructions.")
    shipping_info = models.TextField(blank=True, default="Standard delivery charges apply. Delivery within 3-5 working days.")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    is_available = models.BooleanField(default=True)
    stock = models.PositiveIntegerField(default=0)
    discount_percentage = models.PositiveIntegerField(default=0, help_text="Discount in % (0-100)")
    discount_end_time = models.DateTimeField(null=True, blank=True)

    @property
    def category(self): return self.categories.first()
    
    def get_price(self):
        """Returns discounted price if valid, else normal price"""
        if self.discount_percentage > 0 and self.discount_end_time and self.discount_end_time > timezone.now():
            discount_amount = (self.price * self.discount_percentage) / 100
            return self.price - discount_amount
        return self.price

    def is_discount_active(self):
        return self.discount_percentage > 0 and self.discount_end_time and self.discount_end_time > timezone.now()

    def __str__(self): return self.name

# --- NEW VENDOR MODELS (B2B) ---
class Vendor(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return self.name
    
    def total_products_bought(self):
        return sum(tx.quantity for tx in self.transactions.all())

class VendorTransaction(models.Model):
    vendor = models.ForeignKey(Vendor, related_name='transactions', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    # Admin manually sets vendor discount separately
    vendor_discount_percentage = models.PositiveIntegerField(default=0, help_text="Specific discount for this vendor transaction")
    final_price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Calculate price based on manual vendor discount
        original_price = self.product.price
        discount_amount = (original_price * self.vendor_discount_percentage) / 100
        self.final_price_per_unit = original_price - discount_amount
        self.total_amount = self.final_price_per_unit * self.quantity
        super().save(*args, **kwargs)

    def __str__(self): return f"{self.vendor.name} - {self.product.name}"