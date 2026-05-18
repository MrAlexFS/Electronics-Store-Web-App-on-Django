from django.contrib import admin
from .models import Brand, Category, Product, ProductCopy, Customer, Sale, SoldItem, Return, Supplier, StockReceipt

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

class ProductCopyInline(admin.TabularInline):
    model = ProductCopy
    extra = 1
    fields = ('serial_number', 'status')
    readonly_fields = ('id',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'sku', 'name', 'brand', 'category', 'price', 'warranty_months')
    list_filter = ('brand', 'category')
    search_fields = ('sku', 'name', 'brand__name')
    ordering = ('name',)
    inlines = [ProductCopyInline]
    fieldsets = (
        (None, {'fields': ('sku', 'name', 'brand', 'category')}),
        ('Цены и гарантия', {'fields': ('price', 'warranty_months')}),
        ('Описание', {'fields': ('description',)}),
    )

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'last_name', 'first_name', 'email', 'phone', 'registered_at')
    search_fields = ('last_name', 'email', 'phone')

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'sale_date', 'customer', 'employee', 'total_amount', 'payment_method')
    list_filter = ('payment_method', 'sale_date')
    readonly_fields = ('sale_date',)

@admin.register(SoldItem)
class SoldItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'sale', 'product_copy', 'price_at_sale')

@admin.register(Return)
class ReturnAdmin(admin.ModelAdmin):
    list_display = ('id', 'sold_item', 'return_date', 'reason', 'condition')

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'contact_phone')
    search_fields = ('name',)

@admin.register(StockReceipt)
class StockReceiptAdmin(admin.ModelAdmin):
    list_display = ('id', 'supplier', 'receipt_date', 'total_cost')