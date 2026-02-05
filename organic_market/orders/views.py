from django.conf import settings
from decimal import Decimal
import razorpay 
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse    
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from cart.models import Cart
from products.models import Product
from .models import Order, OrderItem
from accounts.models import Payment
from django.db import transaction
from django.db.models import F


@login_required
def place_order(request):
    if request.method != 'POST':
        return redirect('orders:checkout')

    cart_items = Cart.objects.select_related('product').filter(user=request.user)
    if not cart_items.exists():
        return redirect('cart_detail')

    total = sum(item.subtotal() for item in cart_items)
    payment_method = request.POST.get('payment_method')
    promo_map = {
        'GREEN10': 10,
        'FRESH5': 5,
        'WELCOME15': 15,
    }
    promo_code = request.session.get('promo_code')
    discount_percent = promo_map.get(promo_code, 0)
    discount_amount = (Decimal(total) * Decimal(discount_percent) / Decimal(100)) if discount_percent else Decimal('0')
    final_total = Decimal(total) - discount_amount

    with transaction.atomic():
        product_ids = [item.product_id for item in cart_items]
        locked_products = {
            product.id: product
            for product in Product.objects.select_for_update().filter(id__in=product_ids)
        }
        insufficient = []
        for item in cart_items:
            product = locked_products.get(item.product_id)
            available = product.stock if product else 0
            if available < item.quantity:
                insufficient.append((product.name if product else "Unknown product", available))
        if insufficient:
            names = ", ".join(
                f"{name} (available {available})"
                for name, available in insufficient
            )
            messages.error(request, f"Insufficient stock for: {names}. Please update your cart.")
            return redirect('orders:checkout')

        order = Order.objects.create(
            user=request.user,
            total_amount=final_total,
            payment_method=payment_method,
            status='PAID' if payment_method == 'ONLINE' else 'PENDING'
        )
        Payment.objects.create(
            user=request.user,
            order=order,
            amount=final_total,
            status='SUCCESS' if payment_method == 'ONLINE' else 'PENDING'
        )

        for item in cart_items:
            Product.objects.filter(id=item.product_id).update(stock=F('stock') - item.quantity)
            OrderItem.objects.create(
                order=order,
                product=item.product,
                farmer=item.product.farmer,
                quantity=item.quantity,
                price=item.product.price,
            )

        cart_items.delete()

    request.session.pop('promo_code', None)
    return redirect('orders:my_orders')

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/my_orders.html', {'orders': orders})


@login_required
def track_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    steps = ['PENDING', 'PAID', 'SHIPPED', 'DELIVERED']
    current_index = steps.index(order.status) if order.status in steps else -1
    return render(request, 'orders/track_order.html', {
        'order': order,
        'steps': steps,
        'current_index': current_index,
    })

@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items.exists():
        return redirect('cart_detail')

    total = sum(item.subtotal() for item in cart_items)

    promo_map = {
        'GREEN10': 10,
        'FRESH5': 5,
        'WELCOME15': 15,
    }
    promo_input = (request.GET.get('promo') or '').strip().upper()
    if promo_input:
        if promo_input in promo_map:
            request.session['promo_code'] = promo_input
        else:
            request.session.pop('promo_code', None)

    promo_code = request.session.get('promo_code')
    discount_percent = promo_map.get(promo_code, 0)
    discount_amount = (Decimal(total) * Decimal(discount_percent) / Decimal(100)) if discount_percent else Decimal('0')
    final_total = Decimal(total) - discount_amount

    return render(request, 'orders/checkout.html', {
        'cart_items': cart_items,
        'total': total,
        'promo_code': promo_code,
        'discount_percent': discount_percent,
        'discount_amount': discount_amount,
        'final_total': final_total,
    })

@login_required
def create_razorpay_order(request):
    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items.exists():
        return JsonResponse({'error': 'Cart is empty'})

    total = int(sum(item.subtotal() for item in cart_items) * 100)

    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    razorpay_order = client.order.create({
        'amount': total,
        'currency': 'INR',
        'payment_capture': 1
    })

    return JsonResponse({
        'order_id': razorpay_order['id'],
        'amount': total,
        'key': settings.RAZORPAY_KEY_ID
    })

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status in ['PENDING', 'PAID']:
        order.status = 'CANCELLED'
        order.save()

    return redirect('my_orders')

@login_required
def return_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status == 'DELIVERED':
        order.status = 'RETURNED'
        order.save()

    return redirect('orders:my_orders')

