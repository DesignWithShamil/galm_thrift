from django.contrib import admin
from .models import Category, Order, OrderItem, Product,Quality,Cart,CartItem

admin.site.register(Category)
admin.site.register(Quality)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
