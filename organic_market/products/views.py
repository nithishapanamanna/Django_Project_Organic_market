from pyexpat.errors import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Review
from .forms import ReviewForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.template.loader import render_to_string


# def product_list(request):
#     products = Product.objects.filter(is_approved=True)

#     category = request.GET.get('category')
#     min_price = request.GET.get('min_price')
#     max_price = request.GET.get('max_price')
#     in_stock = request.GET.get('in_stock')

#     if category:
#         products = products.filter(category=category)

#     if min_price:
#         products = products.filter(price__gte=min_price)

#     if max_price:
#         products = products.filter(price__lte=max_price)

#     if in_stock:
#         products = products.filter(stock__gt=0)

#     categories = Product.CATEGORY

#     return render(request, 'products/product_list.html', {
#         'products': products,
#         'categories': categories,
#         'selected_category': category,
#     })


@login_required
def farmer_products(request):
    if request.user.role != 'FARMER':
        return redirect('farmer_login')

    products = Product.objects.filter(farmer=request.user.farmer_profile)
    return render(request, 'products/farmer_products.html', {'products': products})


def product_filter(request):
    products = Product.objects.filter(is_approved=True)

    category = request.GET.get('category')
    if category:
        products = products.filter(category__id=category)

    html = render_to_string('products/product_list_partial.html', {
        'products': products
    })
    return JsonResponse({'html': html})


@login_required
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_approved=True)
    reviews = Review.objects.filter(product=product).order_by('-created_at')
    form = ReviewForm()

    if request.method == 'POST':
        if request.user.role != 'CUSTOMER':
            messages.error(request, "Only customers can leave reviews.")
            return redirect('product_detail', product_id=product.id)

        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, "Review submitted. Thank you!")
            return redirect('product_detail', product_id=product.id)

    return render(request, 'products/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'form': form,
    })
