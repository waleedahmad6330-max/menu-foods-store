from django.contrib import admin
from .models import Order, OrderItem

# Order ke andar Items dikhane ke liye Inline Class
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0

# Main Order Admin Class
class OrderAdmin(admin.ModelAdmin):
    # Admin list mein yeh columns nazar ayenge
    list_display = ('id', 'user', 'first_name', 'total_amount', 'status', 'payment_method', 'is_paid', 'created_at')
    
    # Side mein filters honge
    list_filter = ('status', 'payment_method', 'is_paid', 'created_at')
    
    # Search bar in cheezon par kaam karega
    search_fields = ('id', 'first_name', 'last_name', 'email', 'phone')
    
    # Order kholne par items neeche nazar ayenge
    inlines = [OrderItemInline]

# Register Models
admin.site.register(Order, OrderAdmin)