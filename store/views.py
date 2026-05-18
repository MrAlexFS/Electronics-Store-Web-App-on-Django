from django.shortcuts import render, get_object_or_404
from .models import Product

def product_list(request):
    products = Product.objects.all()
    return render(request, 'store/product_list.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    available_copies = product.copies.filter(status='in_stock')
    return render(request, 'store/product_detail.html', {
        'product': product,
        'available_copies': available_copies,
    })