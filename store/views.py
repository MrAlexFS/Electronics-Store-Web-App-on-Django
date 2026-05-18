from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import Product, ProductCopy, Customer, Sale, SoldItem

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

def cart_detail(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0
    for copy_id, quantity in cart.items():
        copy = get_object_or_404(ProductCopy, pk=copy_id)
        price = copy.product.price
        subtotal = price * quantity
        total += subtotal
        items.append({
            'copy': copy,
            'quantity': quantity,
            'subtotal': subtotal,
        })
    return render(request, 'store/cart_detail.html', {'items': items, 'total': total})

def cart_add(request, copy_id):
    copy = get_object_or_404(ProductCopy, pk=copy_id)
    if copy.status != 'in_stock':
        messages.error(request, 'Этот экземпляр уже недоступен.')
        return redirect('store:product_detail', pk=copy.product.id)
    cart = request.session.get('cart', {})
    cart[str(copy_id)] = cart.get(str(copy_id), 0) + 1
    request.session['cart'] = cart
    messages.success(request, f'Товар "{copy.product.name}" добавлен в корзину.')
    return redirect('store:cart_detail')

def cart_remove(request, item_id):
    cart = request.session.get('cart', {})
    if str(item_id) in cart:
        del cart[str(item_id)]
        request.session['cart'] = cart
        messages.success(request, 'Товар удалён из корзины.')
    return redirect('store:cart_detail')

@transaction.atomic
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, 'Корзина пуста.')
        return redirect('store:product_list')
    
    # Проверяем, что все экземпляры ещё в наличии
    for copy_id in cart.keys():
        copy = ProductCopy.objects.get(pk=copy_id)
        if copy.status != 'in_stock':
            messages.error(request, f'Товар "{copy.product.name}" (серийный номер {copy.serial_number}) уже недоступен.')
            return redirect('store:cart_detail')
    
    if request.method == 'POST':
        # Предположим, что пользователь авторизован или создаём нового покупателя
        # Здесь упростим: считаем, что есть текущий пользователь (или создаём анонимного)
        # Для примера создаём или получаем покупателя по email (можно расширить)
        email = request.POST.get('email')
        last_name = request.POST.get('last_name')
        first_name = request.POST.get('first_name')
        phone = request.POST.get('phone')
        if not all([email, last_name, first_name, phone]):
            messages.error(request, 'Заполните все поля.')
            return render(request, 'store/checkout_form.html', {'cart': cart})
        
        customer, created = Customer.objects.get_or_create(
            email=email,
            defaults={
                'last_name': last_name,
                'first_name': first_name,
                'phone': phone,
            }
        )
        # Создаём продажу
        total_amount = 0
        # Сначала подсчитаем сумму
        for copy_id, quantity in cart.items():
            copy = ProductCopy.objects.get(pk=copy_id)
            total_amount += copy.product.price * quantity
        
        # Предполагаем, что продавец (employee) – первый активный пользователь или суперпользователь
        from django.contrib.auth.models import User
        employee = User.objects.filter(is_superuser=True).first()
        sale = Sale.objects.create(
            customer=customer,
            employee=employee,
            total_amount=total_amount,
            discount=0,
            payment_method='card'   # или выбрать из формы
        )
        # Создаём проданные позиции и меняем статус экземпляров
        for copy_id, quantity in cart.items():
            copy = ProductCopy.objects.get(pk=copy_id)
            copy.status = 'sold'
            copy.save()
            SoldItem.objects.create(
                sale=sale,
                product_copy=copy,
                price_at_sale=copy.product.price
            )
        # Очищаем корзину
        request.session['cart'] = {}
        messages.success(request, 'Заказ успешно оформлен!')
        return redirect('store:order_success', sale_id=sale.id)
    else:
        return render(request, 'store/checkout_form.html', {'cart': cart})

def order_success(request, sale_id):
    sale = get_object_or_404(Sale, pk=sale_id)
    return render(request, 'store/order_success.html', {'sale': sale})