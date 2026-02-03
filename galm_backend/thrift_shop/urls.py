from django.urls import path
from .views import AddToCartView, CartView, CheckoutView, LoginAPI, RegisterAPI, RemoveFromCartView, UpdateCartItemView, order_list_view, product_detail, product_list, category_list, profile_view

urlpatterns = [
    path('products/', product_list),
    path('products/<int:id>/', product_detail),
    path('categories/', category_list),
    path('register/', RegisterAPI.as_view()),
    path('login/', LoginAPI.as_view()),
    path("cart/", CartView.as_view(), name="cart"),
    path("cart/add/", AddToCartView.as_view(), name="add-to-cart"),
    path("cart/remove/", RemoveFromCartView.as_view(), name="remove-from-cart"),
    path("cart/update/", UpdateCartItemView.as_view(), name="update-cart-item"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("profile/", profile_view, name="profile"),
    path("orders/", order_list_view, name="orders"),
]
