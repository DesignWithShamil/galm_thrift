from django.utils import timezone
from rest_framework import viewsets
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from .permissions import IsAdminRole
from django.db import transaction
from .models import Cart, CartItem, Colour, Order, OrderItem, Product, Category, ProductMedia, ProductVariant, Quality, Size,HomeImage,HomeVideo
from .serializers import CartItemSerializer, CartSerializer, ColourSerializer, LoginSerializers, OrderSerializer, ProductMediaSerializer, ProductSerializer, CategorySerializer, ProductVariantSerializer, ProfileUpdateSerializer, QualitySerializer, RegisterSerializer, SizeSerializer, UserSerializer,HomeImageSerializer,HomeVideoSerializer
from rest_framework.pagination import PageNumberPagination
import math
from django.db.models import Q



@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminRole])
def admin_dashboard(request):
    return Response({"message": "Welcome Admin"})





#user detils
# homepage images
# GET view
@api_view(['GET'])
@permission_classes([AllowAny])
def get_home_images(request):
    images = HomeImage.objects.all()
    serializer = HomeImageSerializer(images, many=True)
    return Response(serializer.data)


# POST view (Admin only)
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminRole])
def create_home_image(request):
    serializer = HomeImageSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated, IsAdminRole])
def update_delete_home_image(request, pk):

    try:
        image = HomeImage.objects.get(pk=pk)
    except HomeImage.DoesNotExist:
        return Response(
            {"error": "Home image not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # 🔥 PATCH (Partial Update)
    if request.method == 'PATCH':
        serializer = HomeImageSerializer(
            image,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 🔥 DELETE
    if request.method == 'DELETE':
        image.delete()
        return Response(
            {"message": "Home image deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )


# homepage videos
# GET (Public)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_home_videos(request):
    videos = HomeVideo.objects.all()
    serializer = HomeVideoSerializer(videos, many=True)
    return Response(serializer.data)


# POST (Admin Only)
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminRole])
def create_home_video(request):
    serializer = HomeVideoSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# PATCH & DELETE (Admin Only)
@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated, IsAdminRole])
def update_delete_home_video(request, pk):

    try:
        video = HomeVideo.objects.get(pk=pk)
    except HomeVideo.DoesNotExist:
        return Response(
            {"error": "Home video not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # 🔥 PATCH (Partial Update)
    if request.method == 'PATCH':
        serializer = HomeVideoSerializer(
            video,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 🔥 DELETE
    if request.method == 'DELETE':
        video.delete()
        return Response(
            {"message": "Home video deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )




# GET – List all categories (admin only)
@api_view(['GET'])
@permission_classes([AllowAny])
def category_list(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)


# POST – Create a new category (admin only)
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminRole])
def category_create(request):
    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(serializer.data, status=201)



@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated, IsAdminRole])
def category_update_delete(request, pk):
    try:
        category = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        return Response({"error": "Category not found"}, status=404)

    if request.method == 'PUT':
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({
                "message": "Category updated successfully",
                "data": serializer.data
            })

    if request.method == 'DELETE':
        category.delete()
        return Response({"message": "Category deleted successfully"})

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated, IsAdminRole])
def media_detail(request, pk):

    try:
        media = ProductMedia.objects.get(pk=pk)
    except ProductMedia.DoesNotExist:
        return Response({"error": "Media not found"}, status=404)

    # 🔹 GET single media
    if request.method == 'GET':
        serializer = ProductMediaSerializer(media)
        return Response(serializer.data)

    # 🔹 UPDATE media
    if request.method == 'PUT':
        serializer = ProductMediaSerializer(media, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    # 🔹 DELETE media
    if request.method == 'DELETE':
        if media.file:
            media.file.delete(save=False)  # delete file from folder
        media.delete()
        return Response({"message": "Media deleted successfully"}, status=204)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsAdminRole])
def media_list_create(request):

    if request.method == 'GET':
        media = ProductMedia.objects.all()
        serializer = ProductMediaSerializer(media, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        product_id = request.data.get("product")
        files = request.FILES.getlist("media")

        if not product_id:
            return Response({"error": "Product ID is required"}, status=400)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        created_media = []

        for file in files:
            media_type = "video" if file.content_type.startswith("video") else "image"

            media = ProductMedia.objects.create(
                product=product,
                file=file,
                media_type=media_type,
            )

            created_media.append(ProductMediaSerializer(media).data)

        return Response(created_media, status=201)

        

# GET – List all qualities (allow only)
@api_view(['GET'])
@permission_classes([AllowAny])
def quality_list(request):
    qualities = Quality.objects.all()
    serializer = QualitySerializer(qualities, many=True)
    return Response(serializer.data)


# POST – Create a new quality (admin only)
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminRole])
def quality_create(request):
    serializer = QualitySerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(serializer.data, status=201)

@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated, IsAdminRole])
def quality_update_delete(request, pk):
    try:
        quality = Quality.objects.get(pk=pk)
    except Quality.DoesNotExist:
        return Response({"error": "Quality not found"}, status=404)

    if request.method == 'PUT':
        serializer = QualitySerializer(quality, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"message": "Quality updated successfully", "data": serializer.data})

    if request.method == 'DELETE':
        quality.delete()
        return Response({"message": "Quality deleted successfully"})
    

@api_view(['GET', 'POST'])
def product_variant_list(request):

    if request.method == 'GET':
        variants = ProductVariant.objects.all()
        serializer = ProductVariantSerializer(variants, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':

        product_id = request.data.get("product")
        colour_id = request.data.get("colour_id")
        size_id = request.data.get("size_id")
        stock = int(request.data.get("stock", 0))

        # 🔎 Check if same variant already exists
        existing_variant = ProductVariant.objects.filter(
            product_id=product_id,
            colour_id=colour_id,
            size_id=size_id
        ).first()

        if existing_variant:
            # ✅ Update stock instead of creating duplicate
            existing_variant.stock += stock
            existing_variant.save()

            serializer = ProductVariantSerializer(existing_variant)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # ✅ Create new variant if not exists
        serializer = ProductVariantSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET', 'PUT', 'DELETE'])
def product_variant_detail(request, pk):
    try:
        variant = ProductVariant.objects.get(pk=pk)
    except ProductVariant.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ProductVariantSerializer(variant)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ProductVariantSerializer(variant, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        variant.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)













@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    user = request.user

    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ProfileUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UserSerializer(user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])  # allow entry
def product_detail(request, id):
    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)

    # ✅ PUBLIC GET
    if request.method == 'GET':
        serializer = ProductSerializer(product, context={"request": request})
        return Response(serializer.data)

    # 🔒 ADMIN ONLY for PUT & DELETE
    if not request.user.is_authenticated or not request.user.is_admin:
        return Response(
            {"error": "Admin access required"},
            status=status.HTTP_403_FORBIDDEN
        )

    if request.method == 'PUT':
        serializer = ProductSerializer(
            product,
            data=request.data,
            partial=True,
            context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':
        product.delete()
        return Response(status=204)


@api_view(['GET'])
@permission_classes([AllowAny])
def product_list(request):
    products = Product.objects.all()
    
    
    name = request.GET.get("name")
    type_ = request.GET.get("type")
    category = request.GET.get("category")
    quality = request.GET.get("quality")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    stock_status = request.GET.get("stock")
    latest = request.GET.get("latest")  # ?latest=true

    if name:
        products = products.filter(name__icontains=name)
    if type_:
        products = products.filter(type__iexact=type_)
    if category:
        products = products.filter(category__id=category)
    if quality:
        products = products.filter(quality__id=quality)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    if stock_status == "in":
        products = products.filter(variants__stock__gt=0).distinct()

    elif stock_status == "out":
        products = products.exclude(variants__stock__gt=0).distinct()  

    if latest == "true":
        products = products.order_by('-created_at')[:3]
    else:
        products = products.order_by('-created_at')      

    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def product_create(request):
    serializer = ProductSerializer(
        data=request.data,
        context={"request": request},  # 🔥 REQUIRED
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=201)


# @api_view(['GET'])
# @permission_classes([AllowAny])
# def product_list(request):
#     products = Product.objects.select_related('category','quality').all()  # optimized query
#     serializer = ProductSerializer(products, many=True)
#     return Response(serializer.data)  # make sure this is DRF Response

@api_view(['GET'])
def size_list(request):
    sizes = Size.objects.all()
    serializer = SizeSerializer(sizes, many=True)
    return Response(serializer.data)
@api_view(['GET', 'POST'])
def colour_list(request):
    if request.method =='GET':
        colours = Colour.objects.all()
        serializer = ColourSerializer(colours, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer =ColourSerializer(data =request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'DELETE'])
def colour_detail(request, pk):
    try: 
        colour= Colour.objects.get(pk=pk)
    except Colour.DoesNotExist:
        return Response({"error":"Colour not found"},status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = ColourSerializer(colour, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        colour.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)












# @api_view(['GET'])
# def category_list(request):
#     categories = Category.objects.prefetch_related('product_set').all()
#     serializer = CategorySerializer(categories, many=True)
#     return Response(serializer.data)

class RegisterAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        _data = request.data
        serializer = RegisterSerializer(data=_data)

        if not serializer.is_valid():
            return Response({'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()

        # Assign customer role
        customer_group, _ = Group.objects.get_or_create(name='customer')
        user.groups.add(customer_group)

        return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)

class LoginAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        _data = request.data
        serializer = LoginSerializers(data=_data)

        if not serializer.is_valid():
            return Response({'message': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(
            username=serializer.data['username'],
            password=serializer.data['password']
        )

        if not user:
            return Response({"message": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)

        token, _ = Token.objects.get_or_create(user=user)

        # Get role
        role = user.groups.first().name if user.groups.exists() else "customer"

        return Response({
            'message': 'Login successful',
            'token': token.key,
            'username': user.username,
            'role': role,   # 👈 send role to frontend
            'is_superuser': user.is_superuser
        }, status=status.HTTP_200_OK)

class CartView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get("product_id")
        colour_id = request.data.get("colour_id")
        size_id = request.data.get("size_id")
        quantity = int(request.data.get("quantity", 1))

        if not all([product_id, colour_id, size_id]):
            return Response(
                {"detail": "product_id, colour_id and size_id are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart, _ = Cart.objects.get_or_create(user=request.user)
        product = get_object_or_404(Product, id=product_id)
        colour = get_object_or_404(Colour, id=colour_id)
        size = get_object_or_404(Size, id=size_id)

        variant = get_object_or_404(
            ProductVariant,
            product=product,
            colour=colour,
            size=size,
        )

        if variant.stock < quantity:
            return Response(
                {"detail": "Not enough stock available."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            colour=colour,
            size=size,
        )

        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity

        cart_item.save()

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RemoveFromCartView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        item_id = request.data.get("item_id")
        CartItem.objects.filter(id=item_id, cart__user=request.user).delete()
        return Response({"message": "Item removed"}, status=status.HTTP_200_OK)

class UpdateCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        item_id = request.data.get("item_id")
        quantity = int(request.data.get("quantity"))

        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

        variant = get_object_or_404(
            ProductVariant,
            product=cart_item.product,
            colour=cart_item.colour,
            size=cart_item.size,
        )

        if variant.stock < quantity:
            return Response({"detail": "Not enough stock available."}, status=400)

        cart_item.quantity = quantity
        cart_item.save()

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data)

class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        # 🔥 Check if this is direct buy
        product_id = request.data.get("product_id")
        colour_id = request.data.get("colour_id")
        size_id = request.data.get("size_id")
        quantity = request.data.get("quantity")

        customer_name = request.data.get("customer_name")
        house_name = request.data.get("house_name")
        place = request.data.get("place")
        pincode = request.data.get("pincode")
        mobile_number = request.data.get("mobile_number")

        if not all([customer_name, house_name, place, pincode, mobile_number]):
            return Response({"error": "All address fields are required"}, status=400)

        with transaction.atomic():

            # ========================================
            # ⚡ DIRECT BUY FLOW
            # ========================================
            if product_id and colour_id and size_id:

                quantity = int(quantity or 1)

                product = get_object_or_404(Product, id=product_id)
                colour = get_object_or_404(Colour, id=colour_id)
                size = get_object_or_404(Size, id=size_id)

                variant = get_object_or_404(
                    ProductVariant,
                    product=product,
                    colour=colour,
                    size=size,
                )

                if variant.stock < quantity:
                    return Response({"error": "Not enough stock"}, status=400)

                subtotal = product.price * quantity

                variant.stock -= quantity
                variant.save()

                order = Order.objects.create(
                    user=request.user,
                    customer_name=customer_name,
                    total_price=0,  # temp
                    house_name=house_name,
                    place=place,
                    pincode=pincode,
                    mobile_number=mobile_number,
                    is_paid=False
                )

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    colour=colour,
                    size=size,
                    quantity=quantity,
                    price=product.price
                )

            # ========================================
            # 🛒 CART FLOW
            # ========================================
            else:
                cart = Cart.objects.get(user=request.user)
                cart_items = cart.items.all()

                if not cart_items:
                    return Response({"error": "Cart is empty"}, status=400)

                subtotal = 0

                order = Order.objects.create(
                    user=request.user,
                    customer_name=customer_name,
                    total_price=0,
                    house_name=house_name,
                    place=place,
                    pincode=pincode,
                    mobile_number=mobile_number,
                    is_paid=False
                )

                for item in cart_items:
                    variant = get_object_or_404(
                        ProductVariant,
                        product=item.product,
                        colour=item.colour,
                        size=item.size,
                    )

                    if variant.stock < item.quantity:
                        return Response(
                            {"error": f"Not enough stock for {item.product.name}"},
                            status=400
                        )

                    variant.stock -= item.quantity
                    variant.save()

                    subtotal += item.get_total_price()

                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        colour=item.colour,
                        size=item.size,
                        quantity=item.quantity,
                        price=item.product.price
                    )

                cart_items.delete()

            # ========================================
            # 🚚 DELIVERY CALCULATION (COMMON)
            # ========================================

            if subtotal <= 1000:
                delivery_charge = 80
            elif subtotal <= 2000:
                delivery_charge = 160
            elif subtotal <= 3000:
                delivery_charge = 220
            else:
                delivery_charge = 0

            total = subtotal + delivery_charge

            order.total_price = total
            order.save()

        return Response({
            "message": "Order created successfully",
            "order_id": order.id,
            "subtotal": subtotal,
            "delivery_charge": delivery_charge,
            "total": total
        })
# ---------------- User Order List (paginated) ----------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_list_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    paginator = PageNumberPagination()
    paginator.page_size = 2
    paginated_orders = paginator.paginate_queryset(orders, request)

    serializer = OrderSerializer(paginated_orders, many=True)
    total_items = orders.count()
    total_pages = math.ceil(total_items / paginator.page_size)

    response = paginator.get_paginated_response(serializer.data)
    response.data['total_pages'] = total_pages
    return response


# ---------------- Cancel Order (user or admin) ----------------
class CancelOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        # Admin can cancel any order
        if request.user.is_staff:
            order = get_object_or_404(Order, id=order_id)
        else:
            order = get_object_or_404(Order, id=order_id, user=request.user)

        if order.status == "CANCELLED":
            return Response({"error": "Order already cancelled"}, status=400)

        with transaction.atomic():
            for item in order.items.all():
                variant = ProductVariant.objects.get(
                    product=item.product,
                    colour=item.colour,
                    size=item.size,
                )
                variant.stock += item.quantity
                variant.save()

            order.status = "CANCELLED"
            order.cancelled_at = timezone.now()
            order.save()

        return Response({"message": "Order cancelled successfully"})


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminRole])
def admin_order_list(request):
    # Get optional status filter from query params
    status = request.query_params.get("status")  # e.g., ?status=PLACED

    orders = Order.objects.all().order_by('-created_at')

    if status:
        orders = orders.filter(status=status.upper())

    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

# ---------------- Admin Update Order Status ----------------
@api_view(['PATCH'])
@permission_classes([IsAuthenticated, IsAdminRole])
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    status = request.data.get("status")

    if status not in ["PLACED", "PACKED", "SHIPPED", "DELIVERED", "CANCELLED", "RETURNED"]:
        return Response({"error": "Invalid status"}, status=400)

    order.status = status
    order.save()
    return Response({"message": "Status updated"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def buy_now(request, product_id):

    colour_id = request.data.get("colour_id")
    size_id = request.data.get("size_id")
    quantity = int(request.data.get("quantity", 1))

    if not all([colour_id, size_id]):
        return Response({"error": "Product details required"}, status=400)

    product = get_object_or_404(Product, id=product_id)
    colour = get_object_or_404(Colour, id=colour_id)
    size = get_object_or_404(Size, id=size_id)

    variant = get_object_or_404(
        ProductVariant,
        product=product,
        colour=colour,
        size=size,
    )

    if variant.stock < quantity:
        return Response({"error": "Not enough stock"}, status=400)

    return Response({
        "message": "Proceed to checkout",
        "product_id": product.id,
        "product_name": product.name,
        "product_price": product.price,
        "colour_id": colour.id,
        "colour_name": colour.name,
        "size_id": size.id,
        "size_name": size.name,
        "quantity": quantity,
    })