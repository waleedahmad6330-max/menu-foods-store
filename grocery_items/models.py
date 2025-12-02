from django.db import models
from django.contrib.auth.models import User

# --- CATEGORY ---
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

# --- PRODUCT ---
class Product(models.Model):
    # Multiple Categories Support (ManyToManyField)
    categories = models.ManyToManyField(Category, related_name='products')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    is_available = models.BooleanField(default=True)

    # Compatibility Property (Taake templates mein product.category crash na ho)
    @property
    def category(self):
        return self.categories.first()

    def __str__(self):
        return self.name

# --- ORDER (With Updated Statuses) ---
class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Dispatch', 'Dispatch'),
        ('Delivered', 'Delivered'),
        ('Return', 'Return'),
        ('Cancel', 'Cancel'),
    )
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=50, default='Customer')
    last_name = models.CharField(max_length=50, default='User')
    email = models.EmailField(default='user@example.com')
    phone = models.CharField(max_length=20, default='0000000000')
    
    # Shipping Details
    address = models.TextField(default='Lahore')
    city = models.CharField(max_length=50, default='Lahore')
    
    # Payment & Amount
    payment_method = models.CharField(max_length=20, default='cod')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    
    # Tracking Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    def __str__(self):
        return f"Order {self.id} - {self.status}"

# --- ORDER ITEMS ---
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"

# --- MEMBERSHIP ---
class Membership(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    # Paid Status
    is_paid = models.BooleanField(default=False)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Member: {self.user.username}"