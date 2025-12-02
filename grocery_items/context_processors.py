from .models import Category

def global_data(request):
    # 1. Cart Item Count Logic
    cart = request.session.get('cart', {})
    count = sum(cart.values()) 
    
    # 2. Categories for Navbar (Har page pe categories chahiye hoti hain)
    categories = Category.objects.all()

    return {
        'cart_item_count': count,
        'categories': categories, # Ab views.py mein bar bar categories bhejne ki zaroorat nahi
    }
