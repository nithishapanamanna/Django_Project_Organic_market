from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from urllib3 import request
from .models import CustomerProfile
from django.contrib.auth.decorators import login_required
from orders.models import Order
from products.models import Product
from django.core.paginator import Paginator
from django.db.models import Avg, Count,Q
from .forms import CustomerProfileForm
from .models import CustomerProfile
from django.contrib.auth import get_user_model
User = get_user_model()

def customer_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        if not phone or not address:
            messages.error(request, 'All fields are required')
            return redirect('customer_register')

        if password != password2:
            messages.error(request, 'Passwords do not match')
            return redirect('customer_register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('customer_register')

        user = User.objects.create_user(
            username=username,
            password=password
        )
        user.role = 'CUSTOMER'
        user.save()

        CustomerProfile.objects.create(
            user=user,
            phone=phone,
            address=address
        )

        login(request, user)
        return redirect('customer_dashboard')

    return render(request, 'customer/register.html')


def customer_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user:
            try:
                CustomerProfile.objects.get(user=user)
                login(request, user)
                return redirect('customer_dashboard')
            except CustomerProfile.DoesNotExist:
                pass

        messages.error(request, 'Invalid customer credentials')

    return render(request, 'customer/login.html')


def customer_dashboard(request):
    products_qs = Product.objects.filter(is_approved=True).annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).order_by('-id')
    query = request.GET.get('q') or ''
    if query:
        products_qs = products_qs.filter(
            Q(name__icontains=query) |
            Q(category__icontains=query)
        )
    selected_category = request.GET.get('category') or ''
    if selected_category:
        products_qs = products_qs.filter(category=selected_category)
    paginator = Paginator(products_qs, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'customer/dashboard.html', {
        'products': page_obj,
        'page_obj': page_obj,
        'categories': Product.CATEGORY,
        'selected_category': selected_category,
        'query': query,
    })

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/my_orders.html', {'orders': orders})


@login_required
def customer_profile(request):
    profile, _ = CustomerProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = CustomerProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('customer_profile')
    else:
        form = CustomerProfileForm(instance=profile)

    return render(request, 'customer/profile.html', {'form': form})


@login_required
def customer_delete_account(request):
    if request.method == 'POST':
        user = request.user
        messages.success(request, "Your account has been deleted.")
        user.delete()
        return redirect('home')

    return render(request, 'customer/delete_account.html')

