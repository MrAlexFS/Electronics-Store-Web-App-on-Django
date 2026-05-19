from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.urls import reverse
from autoslug import AutoSlugField

# ---- Модели справочников ----
class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = AutoSlugField(populate_from='name', unique=True, blank=True, editable=False)  # autoslug
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:brand_detail', args=[self.slug])


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = AutoSlugField(populate_from='name', unique=True, blank=True, editable=False)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:category_detail', args=[self.slug])


class Product(models.Model):
    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    warranty_months = models.IntegerField(default=12)
    description = models.TextField(blank=True, null=True)
    slug = AutoSlugField(populate_from='name', unique=True, blank=True, editable=False)
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.sku})"

    def get_absolute_url(self):
        return reverse('store:product_detail', args=[self.slug])


class ProductCopy(models.Model):
    STATUS_CHOICES = [
        ('in_stock', 'На складе'),
        ('reserved', 'Зарезервирован'),
        ('sold', 'Продан'),
        ('returned', 'Возвращён'),
        ('defective', 'Бракованный'),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='copies')
    serial_number = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='in_stock')

    def __str__(self):
        return f"{self.product.name} - {self.serial_number}"


# ---- Единственная модель Customer ----
class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True)
    registered_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class Sale(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Наличные'),
        ('card', 'Карта'),
    ]
    sale_date = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHODS)

    def __str__(self):
        return f"Продажа №{self.id} от {self.sale_date}"


class SoldItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product_copy = models.ForeignKey(ProductCopy, on_delete=models.CASCADE)
    price_at_sale = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_copy} - {self.price_at_sale} руб."


class Return(models.Model):
    sold_item = models.OneToOneField(SoldItem, on_delete=models.CASCADE)
    return_date = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=255)
    condition = models.CharField(max_length=50)

    def __str__(self):
        return f"Возврат по продаже {self.sold_item.sale.id}"


class Supplier(models.Model):
    name = models.CharField(max_length=255, unique=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name


class StockReceipt(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    receipt_date = models.DateField(auto_now_add=True)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Приход от {self.supplier.name} от {self.receipt_date}"