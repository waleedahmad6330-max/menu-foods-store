from django.contrib import admin
from .models import Category, Product, Order, OrderItem, Membership

class ProductAdmin(admin.ModelAdmin):
    # Is se admin panel main Category select karna asaan ho jayega
    # Aap multiple categories select kar sakenge
    filter_horizontal = ('categories',) 
    list_display = ('name', 'price', 'is_available')
    search_fields = ('name',)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'first_name', 'total_amount', 'created_at', 'is_paid')
    list_filter = ('is_paid', 'created_at')
    inlines = [OrderItemInline]

admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Membership)