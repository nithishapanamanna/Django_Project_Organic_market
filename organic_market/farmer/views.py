from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, get_user_model
from products.forms import ProductForm
from .forms import FarmerRegisterForm, FarmerProfileForm
from .models import FarmerProfile
from products.models import Product
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from orders.models import OrderItem
from django.db.models import Sum, F
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
User = get_user_model()

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

    farmer = request.user.farmer_profile  

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

    rejection_notifications = []
    if farmer.rejection_reason:
        rejection_notifications.append({
            'title': 'Account Rejected',
            'message': farmer.rejection_reason,
        })

    rejected_products = products.filter(
        rejection_reason__isnull=False
    ).exclude(rejection_reason='')
    for product in rejected_products:
        rejection_notifications.append({
            'title': f"Product Rejected: {product.name}",
            'message': product.rejection_reason,
        })

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
        'rejection_notifications': rejection_notifications,
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
            product.rejection_reason = None
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
            updated.rejection_reason = None
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


@login_required
def farmer_public_profile(request, farmer_id):
    if request.user.role not in ['CUSTOMER', 'ADMIN', 'FARMER']:
        return HttpResponseForbidden("Access denied")
    try:
        farmer = FarmerProfile.objects.get(id=farmer_id)
    except FarmerProfile.DoesNotExist:
        return render(
            request,
            'farmer/farmer_not_found.html',
            status=404
        )
    return render(request, 'farmer/public_profile.html', {'farmer': farmer})
