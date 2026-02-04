from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from products.forms import ProductForm
from .forms import FarmerRegisterForm, FarmerProfileForm
from .models import FarmerProfile
from products.models import Product
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404
from orders.models import OrderItem
from django.db.models import Sum, F
from django.core.paginator import Paginator
from urllib3 import request
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib import messages

# ---------- FARMER REGISTER ----------
def farmer_register(request):
    if request.method == 'POST':
        user_form = FarmerRegisterForm(request.POST)
        profile_form = FarmerProfileForm(request.POST)

        is_user_valid = user_form.is_valid()
        is_profile_valid = profile_form.is_valid()

        if is_user_valid and is_profile_valid:
            user = user_form.save(commit=False)
            user.role = 'FARMER'
            user.is_active = True
            user.save()

            farmer = profile_form.save(commit=False)
            farmer.user = user
            farmer.is_verified = False
            farmer.save()

            messages.success(request, "Registration successful. Please login.")
            return redirect('farmer_login')

        else:
            messages.error(request, "Registration failed.")
            print(user_form.errors)   # keep for now
            print(profile_form.errors)   # keep for now

    else:
        user_form = FarmerRegisterForm()
        profile_form = FarmerProfileForm()

    return render(request, 'farmer/register.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

# ---------- FARMER LOGIN ----------

def farmer_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if not user:
            messages.error(request, "Invalid credentials")
            return redirect('farmer_login')

        if user.role != 'FARMER':
            messages.error(request, "Not a farmer account")
            return redirect('farmer_login')

        login(request, user)
        return redirect('farmer_dashboard')

    return render(request, 'farmer/login.html')

# ---------- FARMER DASHBOARD ----------
@login_required
def farmer_dashboard(request):
    if request.user.role != 'FARMER':
        return redirect('farmer_login')

    farmer = request.user.farmer_profile  # safe (OneToOne)

    products = Product.objects.filter(farmer=farmer).order_by('-id')
    approved_products = products.filter(is_approved=True)
    pending_products = products.filter(is_approved=False)
    total_products = products.count()
    low_stock = products.filter(stock__lte=50)

    order_items = OrderItem.objects.filter(farmer=farmer)
    paid_items = order_items.filter(order__status__in=['PAID', 'DELIVERED'])
    total_orders = paid_items.values('order').distinct().count()

    revenue = paid_items.aggregate(
        total=Sum(F('price') * F('quantity'))
    )['total'] or 0

    paginator = Paginator(products, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'farmer': farmer,
        'products': page_obj,
        'page_obj': page_obj,
        'approved_products': approved_products,
        'pending_products': pending_products,
        'total_products': total_products,
        'low_stock': low_stock,
        'total_orders': total_orders,
        'revenue': revenue,
    }

    return render(request, 'farmer/dashboard.html', context)



# ---------- ADD PRODUCT ----------
@login_required
def add_product(request):
    if request.user.role != 'FARMER':
        return redirect('farmer_login')

    farmer = request.user.farmer_profile

    # 🚫 Block unverified farmers
    if not farmer.is_verified:
        messages.error(request, "Admin verification required to add products.")
        return redirect('farmer_dashboard')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.farmer = farmer
            product.is_approved = False  # Admin approval
            product.save()
            messages.success(request, "Product submitted for admin approval.")
            return redirect('farmer_dashboard')
    else:
        form = ProductForm()

    return render(request, 'farmer/add_product.html', {'form': form})


@login_required
def edit_product(request, product_id):
    if request.user.role != 'FARMER':
        return redirect('farmer_login')

    farmer = request.user.farmer_profile
    product = get_object_or_404(Product, id=product_id, farmer=farmer)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.is_approved = False
            updated.save()
            messages.success(request, "Product updated and sent for admin approval.")
            return redirect('farmer_dashboard')
    else:
        form = ProductForm(instance=product)

    return render(request, 'farmer/edit_product.html', {'form': form, 'product': product})


@login_required
def delete_product(request, product_id):
    if request.user.role != 'FARMER':
        return redirect('farmer_login')

    farmer = request.user.farmer_profile
    product = get_object_or_404(Product, id=product_id, farmer=farmer)

    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product deleted.")
        return redirect('farmer_dashboard')

    return render(request, 'farmer/delete_product.html', {'product': product})


@login_required
def farmer_profile(request):
    if request.user.role != 'FARMER':
        return redirect('farmer_login')

    farmer = request.user.farmer_profile
    if request.method == 'POST':
        form = FarmerProfileForm(request.POST, request.FILES, instance=farmer)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('farmer_profile')
    else:
        form = FarmerProfileForm(instance=farmer)

    return render(request, 'farmer/profile.html', {'farmer': farmer, 'form': form})
