from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Sum
from decimal import Decimal
from django.http import JsonResponse
import difflib
import stripe

from .models import Category, Product, Order, OrderItem, Membership
from .forms import UserRegisterForm

# --- STRIPE CONFIGURATION ---
stripe.api_key = "sk_test_..."  # Apni Secret Key Yahan Paste Karein

# =========================================
# 1. CUSTOM ADMIN PANEL & DASHBOARD
# =========================================

def is_admin(user): return user.is_superuser

@user_passes_test(is_admin)
def admin_dashboard(request):
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='Pending').count()
    total_revenue = Order.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    recent_orders = Order.objects.all().order_by('-created_at')[:5]
    return render(request, 'custom_admin/dashboard.html', {'total_orders': total_orders, 'pending_orders': pending_orders, 'total_revenue': total_revenue, 'recent_orders': recent_orders})

# --- ORDER MANAGEMENT ---
@user_passes_test(is_admin)
def admin_all_orders(request):
    q = request.GET.get('q')
    orders = Order.objects.all().order_by('-created_at')
    if q: orders = orders.filter(Q(id__icontains=q)|Q(first_name__icontains=q)|Q(last_name__icontains=q))
    return render(request, 'custom_admin/all_orders.html', {'orders': orders, 'query': q})

@user_passes_test(is_admin)
def admin_order_detail(request, order_id):
    print(f"DEBUG: Looking for Order ID: {order_id}") 
    
    try:
        order = Order.objects.get(id=order_id)
        print(f"DEBUG: Found Order: {order}")
    except Order.DoesNotExist:
        print(f"DEBUG: Order ID {order_id} NOT FOUND in Database")
        return render(request, 'store/404.html', {'message': f'Order #{order_id} not found in database'})

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
            
        return redirect('admin_order_detail', order_id=order.id)

    return render(request, 'custom_admin/order_detail.html', {'order': order})

# --- PRODUCT MANAGEMENT (List, Add, Edit, Delete) ---
@user_passes_test(is_admin)
def admin_products_list(request):
    products = Product.objects.all().order_by('-id')
    return render(request, 'custom_admin/products_list.html', {'products': products})

@user_passes_test(is_admin)
def admin_add_product(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        try:
            p = Product.objects.create(
                name=request.POST.get('name'), price=request.POST.get('price'),
                description=request.POST.get('description'), image=request.FILES.get('image')
            )
            p.categories.set(request.POST.getlist('categories')); p.save()
            messages.success(request, "Product Added!")
            return redirect('admin_products_list')
        except Exception as e: messages.error(request, str(e))
    return render(request, 'custom_admin/add_product.html', {'categories': categories})

@user_passes_test(is_admin)
def admin_edit_product(request, pid):
    product = get_object_or_404(Product, id=pid)
    categories = Category.objects.all()
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.price = request.POST.get('price')
        product.description = request.POST.get('description')
        if request.FILES.get('image'): product.image = request.FILES.get('image')
        product.categories.set(request.POST.getlist('categories'))
        product.save()
        messages.success(request, "Product Updated!")
        return redirect('admin_products_list')
    return render(request, 'custom_admin/edit_product.html', {'product': product, 'categories': categories})

@user_passes_test(is_admin)
def admin_delete_product(request, pid):
    Product.objects.filter(id=pid).delete()
    messages.success(request, "Product Deleted")
    return redirect('admin_products_list')

# --- CATEGORY MANAGEMENT (List, Add, Edit, Delete) ---
@user_passes_test(is_admin)
def admin_categories_list(request):
    categories = Category.objects.all()
    return render(request, 'custom_admin/categories_list.html', {'categories': categories})

@user_passes_test(is_admin)
def admin_add_category(request):
    if request.method == 'POST':
        try: Category.objects.create(name=request.POST.get('name'), image=request.FILES.get('image')); messages.success(request, "Category Created!"); return redirect('admin_categories_list')
        except: messages.error(request, "Category exists.")
    return render(request, 'custom_admin/add_category.html')

@user_passes_test(is_admin)
def admin_edit_category(request, cid):
    cat = get_object_or_404(Category, id=cid)
    if request.method == 'POST':
        cat.name = request.POST.get('name')
        if request.FILES.get('image'): cat.image = request.FILES.get('image')
        cat.save()
        messages.success(request, "Category Updated")
        return redirect('admin_categories_list')
    return render(request, 'custom_admin/edit_category.html', {'category': cat})

@user_passes_test(is_admin)
def admin_delete_category(request, cid):
    Category.objects.filter(id=cid).delete()
    messages.success(request, "Category Deleted")
    return redirect('admin_categories_list')

# --- USERS & MEMBERSHIP ---
@user_passes_test(is_admin)
def admin_users(request): return render(request, 'custom_admin/users.html', {'users': User.objects.all().order_by('-date_joined')})
@user_passes_test(is_admin)
def admin_memberships(request): return render(request, 'custom_admin/memberships.html', {'members': Membership.objects.all()})


# =========================================
# 2. USER DASHBOARD
# =========================================
@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/my_orders.html', {'orders': orders})


# =========================================
# 3. CART LOGIC (AJAX READY)
# =========================================
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    pid = str(product_id)
    cart[pid] = cart.get(pid, 0) + 1
    request.session['cart'] = cart
    request.session.modified = True
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'cart_count': sum(cart.values()), 'message': 'Item added to cart!'})
    return redirect('cart_page')

def increase_cart(request, product_id):
    cart = request.session.get('cart', {}); pid = str(product_id)
    if pid in cart: cart[pid]+=1; request.session['cart']=cart; request.session.modified=True
    return redirect('cart_page')

def decrease_cart(request, product_id):
    cart = request.session.get('cart', {}); pid = str(product_id)
    if pid in cart: 
        if cart[pid]>1: cart[pid]-=1
        else: del cart[pid]
    request.session['cart']=cart; request.session.modified=True; return redirect('cart_page')

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {}); pid = str(product_id)
    if pid in cart: del cart[pid]
    request.session['cart']=cart; request.session.modified=True; return redirect('cart_page')

def cart_page(request):
    cart = request.session.get('cart', {}); items = []; subtotal = Decimal('0.00')
    for pid, qty in cart.items():
        try: p=Product.objects.get(id=pid); t=p.price*qty; subtotal+=t; items.append({'product':p, 'quantity':qty, 'total_price':t})
        except: continue
    
    delivery_fee = Decimal('200.00'); discount = Decimal('0.00'); is_member = False
    if request.user.is_authenticated and Membership.objects.filter(user=request.user, is_paid=True).exists():
        is_member = True; delivery_fee = Decimal('0.00'); discount = (subtotal * Decimal('0.10')).quantize(Decimal('0.01'))
    
    if not items: delivery_fee = Decimal('0.00')
    grand_total = subtotal - discount + delivery_fee
    return render(request, 'store/cart.html', {'cart_items':items, 'subtotal':subtotal, 'discount':discount, 'delivery_fee':delivery_fee, 'grand_total':grand_total, 'is_member':is_member})


# =========================================
# 4. CHECKOUT & PAYMENT
# =========================================
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart: return redirect('home')
    total = Decimal('0.00')
    for pid, qty in cart.items():
        try: total += Product.objects.get(id=pid).price * qty
        except: continue

    delivery_fee = Decimal('200.00'); discount = Decimal('0.00'); is_member = False
    if request.user.is_authenticated and Membership.objects.filter(user=request.user, is_paid=True).exists():
        is_member = True; delivery_fee = Decimal('0.00'); discount = (total * Decimal('0.10')).quantize(Decimal('0.01'))
    grand_total = total - discount + delivery_fee

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            first_name=request.POST.get('first_name'), last_name=request.POST.get('last_name'),
            email=request.POST.get('email'), phone=request.POST.get('phone'),
            address=request.POST.get('address'), city=request.POST.get('city'),
            payment_method=payment_method, total_amount=grand_total, status='Pending', is_paid=False
        )
        for pid, qty in cart.items():
            OrderItem.objects.create(order=order, product=Product.objects.get(id=pid), price=Product.objects.get(id=pid).price, quantity=qty)

        if payment_method == 'cod':
            request.session['cart'] = {}; return redirect('success')
        else:
            YOUR_DOMAIN = "http://127.0.0.1:8000"
            try:
                s = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{'price_data': {'currency': 'pkr', 'unit_amount': int(grand_total * 100), 'product_data': {'name': f'Order #{order.id}'}}, 'quantity': 1}],
                    mode='payment', success_url=YOUR_DOMAIN + '/success/', cancel_url=YOUR_DOMAIN + '/cancel/'
                )
                return redirect(s.url, code=303)
            except Exception as e:
                return render(request, 'store/checkout.html', {'total': total, 'discount': discount, 'delivery_fee': delivery_fee, 'grand_total': grand_total, 'is_member': is_member, 'error': str(e)})

    return render(request, 'store/checkout.html', {'total': total, 'discount': discount, 'delivery_fee': delivery_fee, 'grand_total': grand_total, 'is_member': is_member})


# =========================================
# 5. MEMBERSHIP & AUTH
# =========================================
def membership_signup(request):
    FEE = 2000
    if request.method == 'POST':
        email = request.POST.get('email')
        if User.objects.filter(email=email).exists(): messages.error(request, "Email exists."); return redirect('membership')
        try:
            u = User.objects.create_user(username=email.split('@')[0], email=email, password=request.POST.get('password'))
            u.first_name = request.POST.get('first_name'); u.last_name = request.POST.get('last_name'); u.save()
            Membership.objects.create(user=u, phone=request.POST.get('phone'), is_paid=False)
            login(request, u, backend='django.contrib.auth.backends.ModelBackend')
            YOUR_DOMAIN = "http://127.0.0.1:8000"
            s = stripe.checkout.Session.create(payment_method_types=['card'], line_items=[{'price_data': {'currency': 'pkr', 'unit_amount': FEE*100, 'product_data': {'name': 'Premium Membership'}}, 'quantity': 1}], mode='payment', success_url=YOUR_DOMAIN + '/membership-success/', cancel_url=YOUR_DOMAIN + '/cancel/')
            return redirect(s.url, code=303)
        except Exception as e: messages.error(request, str(e)); return redirect('membership')
    return render(request, 'store/membership.html')

def membership_success(request):
    if request.user.is_authenticated:
        try: m = Membership.objects.get(user=request.user); m.is_paid = True; m.save()
        except: pass
    return render(request, 'store/welcome_member.html')

def register_user(request):
    if request.method=='POST':
        form=UserRegisterForm(request.POST)
        if form.is_valid(): u=form.save(commit=False); u.set_password(form.cleaned_data['password']); u.save(); login(request, u, backend='django.contrib.auth.backends.ModelBackend'); return redirect('home')
    return render(request, 'store/register.html', {'form': UserRegisterForm()})
def login_user(request):
    if request.method=='POST':
        u=authenticate(username=request.POST.get('username'),password=request.POST.get('password'))
        if u: login(request, u); return redirect('home')
        else: messages.error(request, "Invalid credentials")
    return render(request, 'store/login.html')
def logout_user(request): logout(request); return redirect('home')


# =========================================
# 6. GENERAL & SEARCH
# =========================================
def home(request): return render(request, 'store/home.html', {'categories': Category.objects.all(), 'products': Product.objects.filter(is_available=True)})
def search(request):
    q = request.GET.get('q'); products = []
    if q:
        db = Product.objects.filter(Q(name__icontains=q)|Q(description__icontains=q)|Q(categories__name__icontains=q)).distinct()
        if db.exists(): products = db
        else:
            all_p = Product.objects.all()
            for p in all_p:
                name_r = difflib.SequenceMatcher(None, p.name.lower(), q.lower()).ratio()
                word_m = any(difflib.SequenceMatcher(None, w, q.lower()).ratio() > 0.6 for w in p.name.lower().split())
                if name_r > 0.5 or word_m: products.append(p)
            products = list(set(products))
    return render(request, 'store/search_results.html', {'products': products, 'query': q})

def category_view(request, category_id): c = get_object_or_404(Category, id=category_id); return render(request, 'store/category.html', {'category': c, 'products': Product.objects.filter(categories=c)})
def product_detail(request, product_id): return render(request, 'store/product_detail.html', {'product': get_object_or_404(Product, id=product_id)})
def welcome_member(request): return render(request, 'store/welcome_member.html')
def success(request): request.session['cart']={}; return render(request, 'store/success.html')
def cancel(request): return render(request, 'store/cancel.html')
def about(request): return render(request, 'store/about.html')