from django.urls import path
from .views import *

urlpatterns = [
    # ------------------ AUTH ------------------
    path('register/', RegisterAPI.as_view(), name='register'),
    path('login/', LoginAPI.as_view(), name='login'), 

    # ------------------ PRODUCTS ------------------
    path('products/', product_list, name='product-list'),
    path('products/<int:pk>/', product_detail, name='product-detail'),
    path('products/create/', product_create, name='product-create'),

    # ------------------ CATEGORIES ------------------
     path('categories/', category_list, name='category-list'),        # GET
    path('categories/create/', category_create, name='category-create'),  # POST
    path('categories/<int:pk>/', category_update_delete, name='category-update-delete'),

    # ------------------ QUALITIES ------------------
    path('qualities/', quality_list, name='quality-list'),
    path('qualities/create/', quality_create, name='quality-create'),
    path('qualities/<int:pk>/', quality_update_delete, name='quality-update-delete'),

    # ------------------ SIZES ------------------
    path('sizes/', size_list, name='size-list'),

    # ------------------ COLOURS ------------------
    path('colours/', colour_list, name='colour-list'),
    path('colours/<int:pk>/', colour_detail, name='colour-detail'),

    # ------------------ MEDIA ------------------
    path('media/', media_list_create, name='media-list-create'),
    path('media/<int:pk>/', media_detail, name='media-detail'),

    # ------------------ PRODUCT VARIANTS ------------------
    path('product-variants/', product_variant_list, name='product-variant-list'),
    path('product-variants/<int:pk>/', product_variant_detail, name='product-variant-detail'),

    # ------------------ CART ------------------
    path("cart/", CartView.as_view(), name="cart"),
    path("cart/add/", AddToCartView.as_view(), name="add-to-cart"),
    path("cart/remove/", RemoveFromCartView.as_view(), name="remove-from-cart"),
    path("cart/update/", UpdateCartItemView.as_view(), name="update-cart-item"),

    # ------------------ CHECKOUT ------------------
    path("checkout/", CheckoutView.as_view(), name="checkout"),

    # ------------------ BUYNOW ------------------
    path("buy-now/<int:product_id>/", buy_now, name="buy_now"),
    # ------------------ PROFILE ------------------
    path("profile/", profile_view, name="profile"),

    # ================== ORDERS (USER) ==================
    path("orders/", order_list_view, name="orders"),  # GET user orders (paginated)
    path("orders/<int:order_id>/cancel/", CancelOrderView.as_view(), name="cancel-order"),  # POST cancel

    # ================== ADMIN ==================
    path('admin-dashboard/', admin_dashboard, name='admin-dashboard'),
    path('admin/orders/', admin_order_list, name='admin-order-list'),  # GET all orders
    path('admin/orders/<int:order_id>/update-status/', update_order_status, name='update-order-status'),  # PATCH
    
     # ================== home imges ==================
    #  GET (Public)
    path('home-images/', get_home_images, name='get-home-images'),

    #  POST (Admin Only)
    path('home-images/create/', create_home_image, name='create-home-image'),

    #  PATCH & DELETE (Admin Only)
    path('home-images/<int:pk>/', update_delete_home_image, name='update-delete-home-image'),
    
     # ================== home vedios ==================
    path('home-videos/', get_home_videos, name='get-home-videos'),
    path('home-videos/create/', create_home_video, name='create-home-video'),
    path('home-videos/<int:pk>/', update_delete_home_video, name='update-delete-home-video'), 

   

]
