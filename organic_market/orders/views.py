from django.conf import settings
from decimal import Decimal
import razorpay 
from django.shortcuts import render, redirect                   
from django.shortcuts import get_object_or_404
from django.http import JsonResponse    
from django.contrib.auth.decorators import login_required
from cart.models import Cart
from products.models import Product
from .models import Order, OrderItem
from django.db.models import F


@login_required
def place_order(request):
    if request.method != 'POST':
        return redirect('orders:checkout')

    cart_items = Cart.objects.filter(user=request.user)
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

    order = Order.objects.create(
        user=request.user,
        total_amount=final_total,
        payment_method=payment_method,
        status='PAID' if payment_method == 'ONLINE' else 'PENDING'
    )

    for item in cart_items:
        Product.objects.filter(id=item.product.id).update(stock=F('stock') - item.quantity)
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

# @login_required
# def place_order(request):
#     cart_items = Cart.objects.filter(user=request.user)

#     if not cart_items.exists():
#         return redirect('cart_detail')

#     total = sum(item.subtotal() for item in cart_items)

#     Order.objects.create(
#         user=request.user,
#         total_amount=total,
#         payment_method='COD'
#     )

#     cart_items.delete()
#     return redirect('orders:my_orders')



@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/my_orders.html', {'orders': orders})

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

