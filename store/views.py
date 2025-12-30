from django.shortcuts import render, get_object_or_404
from django.db.models import Q
import difflib
from .models import Category, Product

# --- CATEGORY VIEW ---
def category_view(request, category_id):
    c = get_object_or_404(Category, id=category_id)
    
    # Logic: Agar parent category hai, to uske bacchon ke products bhi dikhao
    if c.children.exists():
        # Get products from sub-categories + parent itself
        products = Product.objects.filter(categories__in=list(c.children.all()) + [c]).distinct()
    else:
        # Agar child category hai, to sirf uske products
        products = Product.objects.filter(categories=c)

    return render(request, 'store/category.html', {
        'category': c, 
        'products': products, 
        'categories': Category.objects.all()
    })

# --- HOME PAGE ---
def home(request): 
    # Show only available products on home
    return render(request, 'store/home.html', {
        'categories': Category.objects.all(), 
        'products': Product.objects.filter(is_available=True)
    })

# --- PRODUCT DETAIL ---
def product_detail(request, product_id): 
    # Fetch product
    product = get_object_or_404(Product, id=product_id)
    
    # Render template with product data
    # Note: Description, Ingredients, How To Use fields Model se ayenge
    return render(request, 'store/product_detail.html', {
        'product': product, 
        'categories': Category.objects.all()
    })

# --- SEARCH FUNCTIONALITY ---
def search(request):
    q = request.GET.get('q')
    products = []
    
    if q:
        # 1. Exact/Contains Match DB Query
        db = Product.objects.filter(
            Q(name__icontains=q) | 
            Q(description__icontains=q) | 
            Q(categories__name__icontains=q)
        ).distinct()
        
        if db.exists(): 
            products = db
        else:
            # 2. Fuzzy Matching (Agar spelling mistake ho)
            all_p = Product.objects.all()
            for p in all_p:
                # Name Match Ratio
                name_r = difflib.SequenceMatcher(None, p.name.lower(), q.lower()).ratio()
                # Word Match Logic
                word_m = any(difflib.SequenceMatcher(None, w, q.lower()).ratio() > 0.6 for w in p.name.lower().split())
                
                if name_r > 0.5 or word_m: 
                    products.append(p)
            
            # Remove duplicates if any
            products = list(set(products))
            
    return render(request, 'store/search_results.html', {
        'products': products, 
        'query': q
    })

# --- STATIC PAGES ---
def about(request): 
    return render(request, 'store/about.html')