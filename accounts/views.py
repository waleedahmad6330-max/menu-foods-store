from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import UserRegisterForm, MembershipSignupForm
from .models import Membership
from store.models import Category
import stripe
import os
from dotenv import load_dotenv

# --- LOAD ENVIRONMENT VARIABLES ---
load_dotenv() # Yeh line .env file ko parhti hai

# Key ko .env se uthao
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# --- AUTHENTICATION ---

def login_view(request):
    if request.method == 'POST':
        u = authenticate(username=request.POST.get('username'), password=request.POST.get('password'))
        if u: 
            login(request, u)
            return redirect('home')
        messages.error(request, "Invalid credentials")
    return render(request, 'accounts/login.html', {'categories': Category.objects.all()})

def logout_view(request):
    logout(request)
    return redirect('home')

def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            u = form.save(commit=False)
            u.username = form.cleaned_data['email'].split('@')[0]
            u.set_password(form.cleaned_data['password'])
            u.save()
            login(request, u, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form, 'categories': Category.objects.all()})


# --- MEMBERSHIP LOGIC (SECURE FLOW) ---

def membership_signup(request):
    FEE = 2000
    
    if request.method == 'POST':
        form = MembershipSignupForm(request.POST)
        
        # 1. Check if email exists
        email = request.POST.get('email')
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists. Please login instead.")
            return render(request, 'accounts/membership.html', {'form': form, 'categories': Category.objects.all()})

        if form.is_valid():
            try:
                # 2. IMPORTANT: User abhi Create NAHI karna.
                # Data ko Session mein save karein (Temporary)
                request.session['membership_data'] = {
                    'first_name': form.cleaned_data['first_name'],
                    'last_name': form.cleaned_data['last_name'],
                    'email': form.cleaned_data['email'],
                    'password': form.cleaned_data['password'], 
                    'phone': request.POST.get('phone')
                }

                # 3. Stripe Session Create Karein
                YOUR_DOMAIN = f"{request.scheme}://{request.get_host()}"
                
                checkout_session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price_data': {
                            'currency': 'pkr', 
                            'unit_amount': FEE * 100, 
                            'product_data': {'name': 'Menu Premium Membership'}
                        },
                        'quantity': 1,
                    }],
                    mode='payment',
                    # Success hone par yahan jayega
                    success_url=YOUR_DOMAIN + '/auth/membership-success/',
                    # Cancel hone par yahan jayega
                    cancel_url=YOUR_DOMAIN + '/payments/membership-cancel/', 
                )
                return redirect(checkout_session.url, code=303)

            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
    else:
        form = MembershipSignupForm()
        
    return render(request, 'accounts/membership.html', {'form': form, 'categories': Category.objects.all()})


def membership_success(request):
    # 4. Payment Success ke baad User Create hoga
    data = request.session.get('membership_data')
    
    if data:
        try:
            # Dobara check karein duplicate email
            if User.objects.filter(email=data['email']).exists():
                u = User.objects.get(email=data['email'])
            else:
                # User Create Karein
                username = data['email'].split('@')[0]
                if User.objects.filter(username=username).exists():
                    username += str(User.objects.last().id)

                u = User.objects.create_user(username=username, email=data['email'], password=data['password'])
                u.first_name = data['first_name']
                u.last_name = data['last_name']
                u.save()

            # Membership Active Karein
            Membership.objects.create(user=u, phone=data['phone'], is_paid=True, amount_paid=2000)
            
            # Ab User ko Login karwayen
            login(request, u, backend='django.contrib.auth.backends.ModelBackend')
            
            # Session saaf kar dein
            del request.session['membership_data']

        except Exception as e:
            pass

    return render(request, 'accounts/welcome_member.html', {'categories': Category.objects.all()})