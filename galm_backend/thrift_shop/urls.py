from django.urls import path
from .views import product_list, category_list

urlpatterns = [
    path('products/', product_list),
    path('categories/', category_list),
]
