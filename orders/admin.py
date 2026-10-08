from django.contrib import admin
from .models import Order, Product, RefundRequest

class ProductAdmin(admin.ModelAdmin):
    list_display= ['name', 'description', 'price', 'category', 'in_stock']

class OrderAdmin(admin.ModelAdmin):
    list_display= ['user', 'product_name', 'status', 'amount', 'carrier', 'tracking_number']

class RefundRequestAdmin(admin.ModelAdmin):
    list_display= ['order','user', 'reason', 'status', 'created_at']

# Register your models here.
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(RefundRequest, RefundRequestAdmin)