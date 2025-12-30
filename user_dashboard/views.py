from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from orders.models import Order
from store.models import Category 

@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'user_dashboard/my_orders.html', {'orders': orders, 'categories': Category.objects.all()})