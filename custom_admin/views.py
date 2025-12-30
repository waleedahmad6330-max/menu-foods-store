from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone
from django.contrib.auth.models import User

# --- IMPORTANT: Ensure these imports are correct based on your app names ---
from store.models import Product, Category, Vendor, VendorTransaction
from orders.models import Order
from accounts.models import Membership # Ensure 'accounts' app exists

def is_admin(u): return u.is_superuser

# --- DASHBOARD ---
@user_passes_test(is_admin)
def admin_dashboard(request):
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='Pending').count()
    total_revenue = Order.objects.filter(is_paid=True).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    recent_orders = Order.objects.all().order_by('-created_at')[:5]
    total_vendors = Vendor.objects.count()
    
    return render(request, 'custom_admin/dashboard.html', {
        'total_orders': total_orders, 
        'pending_orders': pending_orders,
        'total_revenue': total_revenue, 
        'recent_orders': recent_orders,
        'total_vendors': total_vendors
    })

# --- ALL ORDERS (This was missing causing the error) ---
@user_passes_test(is_admin)
def admin_all_orders(request):
    q = request.GET.get('q')
    orders = Order.objects.all().order_by('-created_at')
    if q:
        orders = orders.filter(Q(id__icontains=q)|Q(first_name__icontains=q))
    return render(request, 'custom_admin/all_orders.html', {'orders': orders})

# --- ORDER DETAIL ---
@user_passes_test(is_admin)
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        if 'update_status' in request.POST:
            order.status = request.POST.get('status')
            order.save()
            messages.success(request, f"Order Status Updated")
        elif 'update_address' in request.POST:
            order.address = request.POST.get('address')
            order.city = request.POST.get('city')
            order.phone = request.POST.get('phone')
            order.save()
            messages.success(request, "Address Updated")
        elif 'mark_paid' in request.POST:
            order.is_paid = True
            order.save()
            messages.success(request, "Payment Confirmed!")
        return redirect('admin_order_detail', order_id=order.id)
    return render(request, 'custom_admin/order_detail.html', {'order': order})

# --- PRODUCTS LIST ---
@user_passes_test(is_admin)
def admin_products_list(request):
    return render(request, 'custom_admin/products_list.html', {'products': Product.objects.all()})

# --- ADD PRODUCT ---
@user_passes_test(is_admin)
def admin_add_product(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        try:
            p = Product.objects.create(
                name=request.POST.get('name'),
                price=request.POST.get('price'),
                description=request.POST.get('description'),
                 ingredients=request.POST.get('ingredients'),
                how_to_use=request.POST.get('how_to_use'),
                shipping_info=request.POST.get('shipping_info'),
                image=request.FILES.get('image'),
                stock=request.POST.get('stock', 0),
                discount_percentage=request.POST.get('discount_percentage', 0),
                discount_end_time=request.POST.get('discount_end_time') or None
            )
            p.categories.set(request.POST.getlist('categories'))
            p.save()
            messages.success(request, "Product Added!")
            return redirect('admin_products_list')
        except Exception as e:
            messages.error(request, str(e))
    return render(request, 'custom_admin/add_product.html', {'categories': categories})

# --- EDIT PRODUCT ---
@user_passes_test(is_admin)
def admin_edit_product(request, pid):
    p = get_object_or_404(Product, id=pid)
    categories = Category.objects.all()
    if request.method == 'POST':
        p.name=request.POST.get('name')
        p.price=request.POST.get('price')
        p.description=request.POST.get('description')
        p.ingredients = request.POST.get('ingredients')
        p.how_to_use = request.POST.get('how_to_use')
        p.shipping_info = request.POST.get('shipping_info')
        if request.FILES.get('image'): p.image=request.FILES.get('image')
        p.stock = request.POST.get('stock', 0)
        p.discount_percentage = request.POST.get('discount_percentage', 0)
        end_time = request.POST.get('discount_end_time')
        if end_time: p.discount_end_time = end_time
        elif request.POST.get('clear_timer'): p.discount_end_time = None
        p.categories.set(request.POST.getlist('categories'))
        p.save()
        messages.success(request, "Product Updated")
        return redirect('admin_products_list')
    return render(request, 'custom_admin/edit_product.html', {'product': p, 'categories': categories})

# --- DELETE PRODUCT ---
@user_passes_test(is_admin)
def admin_delete_product(request, pid):
    Product.objects.filter(id=pid).delete()
    messages.success(request, "Product Deleted")
    return redirect('admin_products_list')

# --- CATEGORIES ---
@user_passes_test(is_admin)
def admin_categories_list(request):
    return render(request, 'custom_admin/categories_list.html', {'categories': Category.objects.all()})

@user_passes_test(is_admin)
def admin_add_category(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            image = request.FILES.get('image')
            parent_ids = request.POST.getlist('parents')
            cat = Category.objects.create(name=name, image=image)
            if parent_ids: cat.parents.set(parent_ids); cat.save()
            messages.success(request, "Category Created!")
            return redirect('admin_categories_list')
        except Exception as e: messages.error(request, str(e))
    return render(request, 'custom_admin/add_category.html', {'categories': Category.objects.all()})

@user_passes_test(is_admin)
def admin_edit_category(request, cid):
    c = get_object_or_404(Category, id=cid)
    all_cats = Category.objects.exclude(id=cid)
    if request.method == 'POST':
        c.name = request.POST.get('name')
        if request.FILES.get('image'): c.image = request.FILES.get('image')
        c.parents.set(request.POST.getlist('parents'))
        c.save()
        messages.success(request, "Category Updated")
        return redirect('admin_categories_list')
    return render(request, 'custom_admin/edit_category.html', {'category': c, 'categories': all_cats})

@user_passes_test(is_admin)
def admin_delete_category(request, cid):
    Category.objects.filter(id=cid).delete()
    messages.success(request, "Category Deleted")
    return redirect('admin_categories_list')

# --- USERS & MEMBERSHIPS ---
@user_passes_test(is_admin)
def admin_users(request):
    return render(request, 'custom_admin/users.html', {'users': User.objects.all().order_by('-date_joined')})

@user_passes_test(is_admin)
def admin_memberships(request):
    return render(request, 'custom_admin/memberships.html', {'members': Membership.objects.all()})

# --- VENDORS (B2B) ---
@user_passes_test(is_admin)
def admin_vendors_list(request):
    return render(request, 'custom_admin/vendors_list.html', {'vendors': Vendor.objects.all()})

@user_passes_test(is_admin)
def admin_add_vendor(request):
    if request.method == 'POST':
        Vendor.objects.create(
            name=request.POST.get('name'),
            phone=request.POST.get('phone'),
            address=request.POST.get('address')
        )
        messages.success(request, "Vendor Added")
        return redirect('admin_vendors_list')
    return render(request, 'custom_admin/add_vendor.html')

@user_passes_test(is_admin)
def admin_vendor_detail(request, vid):
    vendor = get_object_or_404(Vendor, id=vid)
    products = Product.objects.all()
    
    if request.method == 'POST':
        pid = request.POST.get('product_id')
        qty = int(request.POST.get('quantity'))
        vendor_discount = int(request.POST.get('vendor_discount', 0))
        
        product = get_object_or_404(Product, id=pid)
        
        if product.stock >= qty:
            VendorTransaction.objects.create(
                vendor=vendor,
                product=product,
                quantity=qty,
                vendor_discount_percentage=vendor_discount
            )
            product.stock -= qty
            product.save()
            messages.success(request, f"Assigned {qty} {product.name} to {vendor.name}")
        else:
            messages.error(request, f"Not enough stock! Available: {product.stock}")
            
        return redirect('admin_vendor_detail', vid=vid)
        
    return render(request, 'custom_admin/vendor_detail.html', {'vendor': vendor, 'products': products})