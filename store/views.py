from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Product, Category, Brand

def product_list(request):
    # Получаем все товары
    
    products = Product.objects.all().order_by('id')

    # Поиск (GET-параметр 'q')
    search_query = request.GET.get('q', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(brand__name__icontains=search_query)
        )

    # Фильтр по категории
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)

    # Фильтр по бренду
    brand_id = request.GET.get('brand')
    if brand_id:
        products = products.filter(brand_id=brand_id)

    # Пагинация
    paginator = Paginator(products, 9)  # 9 товаров на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Списки для фильтров (все категории и бренды)
    categories = Category.objects.all()
    brands = Brand.objects.all()

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'selected_category': category_id,
        'selected_brand': brand_id,
        'categories': categories,
        'brands': brands,
    }
    return render(request, 'pages/product_list.html', context)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'pages/product_detail.html', {'product': product})

from django.http import HttpResponse
from django.shortcuts import redirect

def cart_detail(request):
    return HttpResponse("Страница корзины в разработке.")

def cart_add(request, copy_id):
    return redirect('store:product_list')

def cart_remove(request, item_id):
    return redirect('store:product_list')

def checkout(request):
    return HttpResponse("Оформление заказа временно недоступно.")

def order_success(request, sale_id):
    return HttpResponse(f"Заказ №{sale_id} успешно оформлен.")

def profile(request):
    return HttpResponse("Личный кабинет в разработке.")

def register(request):
    return HttpResponse("Регистрация временно недоступна. Используйте админку.")