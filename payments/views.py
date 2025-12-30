from django.shortcuts import render
from store.models import Category
from orders.models import Order


def success(request): 
    request.session['cart'] = {}
    return render(request, 'orders/success.html', {'categories': Category.objects.all()})

def success(request): 
    request.session['cart'] = {}
    return render(request, 'orders/success.html', {'categories': Category.objects.all()})

# --- FIX: Order Delete Logic ---
def cancel(request, order_id=None):
    if order_id:
        try:
            # Wo order dhoondo jo pay nahi hua aur delete kar do
            order = Order.objects.get(id=order_id, is_paid=False)
            order.delete()
        except Order.DoesNotExist:
            pass 
            
    return render(request, 'orders/cancel.html', {'categories': Category.objects.all()})