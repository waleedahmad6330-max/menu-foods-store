from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from store.models import Product, Category
from accounts.models import Membership
from .models import Order, OrderItem
import stripe
import os
from dotenv import load_dotenv
load_dotenv()

# Stripe API Key
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')


def calculate_cart_totals(request, cart):
    subtotal = Decimal('0.00')
    items_count = 0
    for pid, qty in cart.items():
        try:
            p = Product.objects.get(id=pid)
            price = p.get_price() if hasattr(p, 'get_price') else p.price
            subtotal += price * qty
            items_count += qty
        except: continue
    
    delivery = Decimal('200.00')
    discount = Decimal('0.00')
    FREE_DELIVERY_THRESHOLD = Decimal('2500.00')
    shortfall = Decimal('0.00')

    if request.user.is_authenticated and Membership.objects.filter(user=request.user, is_paid=True).exists():
        delivery = Decimal('0.00')
        discount = (subtotal * Decimal('0.10')).quantize(Decimal('0.01'))
    elif subtotal >= FREE_DELIVERY_THRESHOLD:
        delivery = Decimal('0.00')
    else:
        if subtotal > 0: shortfall = FREE_DELIVERY_THRESHOLD - subtotal

    if items_count == 0:
        delivery = Decimal('0.00')
        shortfall = Decimal('0.00')
    
    grand_total = subtotal - discount + delivery
    return subtotal, delivery, discount, grand_total, items_count, shortfall

# ==========================================
# --- UPDATED: ADD TO CART FUNCTION ---
# ==========================================
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    pid = str(product_id)
    
    # 1. Quantity Get Karo
    quantity = 1
    if request.method == 'POST':
        try: 
            quantity = int(request.POST.get('quantity', 1))
        except: 
            quantity = 1
            
    # 2. Check Stock
    current_qty = cart.get(pid, 0)
    
    # Agar stock available hai
    if product.stock >= (current_qty + quantity):
        cart[pid] = current_qty + quantity
        request.session['cart'] = cart
        request.session.modified = True
        
        # --- AJAX REQUEST HANDLING ---
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success', 
                'cart_count': sum(cart.values()), 
                'message': f'Successfully added {product.name}!'
            })
            
        # --- NORMAL REQUEST (FALLBACK) ---
        # Agar JS disable ho to yeh chalega
        action = request.POST.get('action')
        if action == 'buy_now':
            return redirect('cart_page') # Redirect directly to cart
            
        messages.success(request, f"Added {quantity} {product.name} to cart.")
        return redirect(request.META.get('HTTP_REFERER', 'home'))
        
    else:
        # --- STOCK ERROR HANDLING ---
        msg = f"Out of Stock! Only {product.stock} items available."
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
             return JsonResponse({'status': 'error', 'message': msg}, status=400)
        
        messages.error(request, msg)
        return redirect(request.META.get('HTTP_REFERER', 'home'))

# --- CART UPDATES ---
def update_cart_action(request, product_id, action):
    cart = request.session.get('cart', {})
    pid = str(product_id)
    if pid in cart:
        if action == 'increase': 
            try:
                p = Product.objects.get(id=pid)
                if p.stock > cart[pid]: cart[pid] += 1
                else: pass 
            except: pass
        elif action == 'decrease':
            if cart[pid] > 1: cart[pid] -= 1
            else: del cart[pid]
        elif action == 'remove': del cart[pid]
    request.session['cart'] = cart
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        sub, delivery, disc, total, count, shortfall = calculate_cart_totals(request, cart)
        item_qty = cart.get(pid, 0)
        item_total = 0
        if pid in cart:
            p = Product.objects.get(id=pid)
            price = p.get_price() if hasattr(p, 'get_price') else p.price
            item_total = price * item_qty
        
        return JsonResponse({
            'status': 'success', 'cart_count': count, 'subtotal': str(sub),
            'delivery': str(delivery), 'discount': str(disc), 'total': str(total),
            'shortfall': str(shortfall), 'item_qty': item_qty, 'item_total': str(item_total)
        })
    return redirect('cart_page')

def increase_cart(request, product_id): return update_cart_action(request, product_id, 'increase')
def decrease_cart(request, product_id): return update_cart_action(request, product_id, 'decrease')
def remove_from_cart(request, product_id): return update_cart_action(request, product_id, 'remove')

def cart_page(request):
    cart = request.session.get('cart', {})
    items = []
    sub, delivery, disc, total, count, shortfall = calculate_cart_totals(request, cart)
    is_member = request.user.is_authenticated and Membership.objects.filter(user=request.user, is_paid=True).exists()

    for pid, qty in cart.items():
        try:
            p = Product.objects.get(id=pid)
            price = p.get_price() if hasattr(p, 'get_price') else p.price
            items.append({'product': p, 'quantity': qty, 'total_price': price * qty})
        except: continue
        
    return render(request, 'orders/cart.html', {
        'cart_items': items, 'subtotal': sub, 'discount': disc,
        'delivery_fee': delivery, 'grand_total': total, 'is_member': is_member,
        'shortfall': shortfall, 'categories': Category.objects.all()
    })

def checkout(request):
    cart = request.session.get('cart', {})
    if not cart: return redirect('home')
    sub, delivery, disc, total, count, shortfall = calculate_cart_totals(request, cart)
    is_member = request.user.is_authenticated and Membership.objects.filter(user=request.user, is_paid=True).exists()

    if request.method == 'POST':
        for pid, qty in cart.items():
            prod = Product.objects.get(id=pid)
            if prod.stock < qty:
                messages.error(request, f"Sorry, {prod.name} is out of stock.")
                return redirect('cart_page')

        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            first_name=request.POST.get('first_name'), last_name=request.POST.get('last_name'),
            email=request.POST.get('email'), phone=request.POST.get('phone'),
            address=request.POST.get('address'), city=request.POST.get('city'),
            payment_method=request.POST.get('payment_method'), total_amount=total
        )
        
        for pid, qty in cart.items():
            prod = Product.objects.get(id=pid)
            price = prod.get_price() if hasattr(prod, 'get_price') else prod.price
            OrderItem.objects.create(order=order, product=prod, price=price, quantity=qty)
            prod.stock -= qty
            prod.save()

        if order.payment_method == 'cod':
            request.session['cart'] = {}
            return redirect('payment_success', order_id=order.id)
        else:
            YOUR_DOMAIN = f"{request.scheme}://{request.get_host()}"
            try:
                s = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{'price_data': {'currency': 'pkr', 'unit_amount': int(total * 100), 'product_data': {'name': f'Order #{order.id}'}}, 'quantity': 1}],
                    mode='payment',
                    success_url=f"{YOUR_DOMAIN}/shop/payment-success/{order.id}/",
                    cancel_url=f"{YOUR_DOMAIN}/payments/cancel/{order.id}/"
                )
                return redirect(s.url, code=303)
            except Exception as e:
                order.delete()
                # Restore stock logic would go here
                return render(request, 'orders/checkout.html', {'total': sub, 'discount': disc, 'delivery_fee': delivery, 'grand_total': total, 'error': str(e)})

    return render(request, 'orders/checkout.html', {'total': sub, 'discount': disc, 'delivery_fee': delivery, 'grand_total': total, 'is_member': is_member, 'categories': Category.objects.all()})

def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.payment_method == 'stripe':
        order.is_paid = True
        order.save()
    request.session['cart'] = {}
    return render(request, 'orders/success.html', {'categories': Category.objects.all()})

@login_required(login_url='login')
def my_orders(request):
    return render(request, 'orders/my_orders.html', {'orders': Order.objects.filter(user=request.user).order_by('-created_at'), 'categories': Category.objects.all()})