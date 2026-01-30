from django.contrib import admin
from .models import Category, Product,Quality

admin.site.register(Category)
admin.site.register(Quality)
admin.site.register(Product)
