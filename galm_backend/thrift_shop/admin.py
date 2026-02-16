from django.contrib import admin
from .models import Category, Order, OrderItem, Product, ProductMedia,Quality,Cart,CartItem,Size,ProductVariant,Colour

admin.site.register(Category)
admin.site.register(Quality)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ProductVariant)
admin.site.register(Colour)
admin.site.register(Size)
admin.site.register(ProductMedia)

