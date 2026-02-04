from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import logout as auth_logout,authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from farmer.models import FarmerProfile
from products.models import Product
from orders.models import Order
from django.db.models import Sum,Count
from .models import Payment

from django.contrib.auth import get_user_model
User = get_user_model()

from django.shortcuts import get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from .decorators import admin_required

def home(request):
    return render(request, 'home.html')

def login_choice(request):
    return render(request, 'accounts/login_choice.html')


def user_logout(request):
    auth_logout(request)   # Django logout
    messages.info(request, 'You have logged out successfully.')
    return redirect('home')

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user and user.role == 'ADMIN':
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid admin credentials')

    return render(request, 'accounts/admin_login.html')


@login_required
def admin_dashboard(request):
    if request.user.role != 'ADMIN':
        return HttpResponseForbidden("Access denied")

    # Notifications
    pending_farmers = FarmerProfile.objects.filter(is_verified=False)
    pending_products = Product.objects.filter(is_approved=False)
    pending_orders = Order.objects.filter(status='PENDING')
    pending_payments = Payment.objects.filter(status='PENDING')

    # Stats
    total_farmers = FarmerProfile.objects.count()
    verified_farmers = FarmerProfile.objects.filter(is_verified=True).count()
    total_products = Product.objects.count()
    approved_products = Product.objects.filter(is_approved=True).count()
    total_orders = Order.objects.count()
    approved_orders = Order.objects.exclude(status='PENDING').count()

    revenue = Order.objects.filter(
        status__in=['PAID', 'DELIVERED']
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    status_data = {
        'pending': Order.objects.filter(status='PENDING').count(),
        'shipped': Order.objects.filter(status='SHIPPED').count(),
        'delivered': Order.objects.filter(status='DELIVERED').count(),
        'cancelled': Order.objects.filter(status='CANCELLED').count(),
    }
    status_total = sum(status_data.values())

    return render(request, 'accounts/admin_dashboard.html', {
        # notifications
        'pending_farmer_count': pending_farmers.count(),
        'pending_product_count': pending_products.count(),
        'pending_order_count': pending_orders.count(),
        'pending_payment_count': pending_payments.count(),

        # lists
        'pending_farmers': pending_farmers,

        # stats
        'total_farmers': total_farmers,
        'verified_farmers': verified_farmers,
        'total_products': total_products,
        'approved_products': approved_products,
        'total_orders': total_orders,
        'approved_orders': approved_orders,
        'revenue': revenue,
        'status_data': status_data,
        'status_total': status_total,
    })

@staff_member_required
def verify_farmers(request):
    if request.user.role != 'ADMIN':
        return HttpResponseForbidden("Access Denied")

    farmers = FarmerProfile.objects.all()
    return render(request, 'accounts/verify_farmers.html', {
        'farmers': farmers
    })

@staff_member_required
def approve_farmer(request, farmer_id):
    farmer = get_object_or_404(FarmerProfile, id=farmer_id)
    farmer.is_verified = True
    farmer.save()
    messages.success(request, "Farmer approved successfully")
    return redirect('verify_farmers')


@login_required
def reject_farmer(request, farmer_id):
    if request.user.role != 'ADMIN':
        return HttpResponseForbidden("Access Denied")
    farmer = get_object_or_404(FarmerProfile, id=farmer_id)
    farmer.is_verified = False
    farmer.save()
    messages.warning(request, "Farmer rejected")
    return redirect('verify_farmers')


@staff_member_required
def pending_farmers(request):
    farmers = FarmerProfile.objects.filter(is_verified=False)
    return render(request, 'admin/pending_farmers.html', {
        'farmers': farmers
    })

@staff_member_required
def approve_products(request):
    products = Product.objects.filter(is_approved=False)

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        Product.objects.filter(id=product_id).update(is_approved=True)
        messages.success(request, "Product approved")
        return redirect('approve_products')

    return render(request, 'accounts/approve_products.html', {
        'products': products
    })

@staff_member_required
def reject_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.error(request, "Product rejected")
    return redirect('approve_products')
from orders.models import Order

@staff_member_required
def manage_orders(request):
    orders = Order.objects.all().order_by("-created_at")

    if request.method == "POST":
        order_id = request.POST.get("order_id")
        order = Order.objects.get(id=order_id)
        order.status = "DELIVERED"
        order.save()
        return redirect("manage_orders")

    return render(request, "accounts/manage_orders.html", {
        "orders": orders
    })
    
@login_required
def manage_users(request):
    if request.user.role != 'ADMIN':
        return HttpResponseForbidden("Access denied")

    role = request.GET.get('role')

    users = User.objects.all().order_by('-date_joined')
    if role:
        users = users.filter(role=role)

    return render(request, 'accounts/manage_users.html', {
        'users': users,
        'selected_role': role,
    })

@login_required
def toggle_user_status(request, user_id):
    if request.user.role != 'ADMIN':
        return HttpResponseForbidden("Access denied")

    user = get_object_or_404(User, id=user_id)

    # Prevent admin disabling themselves
    if user == request.user:
        messages.error(request, "You cannot disable yourself.")
        return redirect('manage_users')

    user.is_active = not user.is_active
    user.save()

    status = "activated" if user.is_active else "deactivated"
    messages.success(request, f"User {user.username} {status} successfully.")

    return redirect('manage_users')

@admin_required
def manage_payments(request):
    payments = Payment.objects.all().order_by("-created_at")
    return render(request, "accounts/payments.html", {
        "payments": payments
    })

