from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from .models import Cart, CartItem, Order, OrderItem, Product, Category
from .serializers import CartItemSerializer, CartSerializer, LoginSerializers, OrderSerializer, ProductSerializer, CategorySerializer, RegisterSerializer, UserSerializer


#user detils
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def product_detail(request, id):
    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)

    serializer = ProductSerializer(product)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def product_list(request):
    products = Product.objects.select_related('category','quality').all()  # optimized query
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)  # make sure this is DRF Response


@api_view(['GET'])
def category_list(request):
    categories = Category.objects.prefetch_related('product_set').all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)

class RegisterAPI(APIView):
      permission_classes=[AllowAny]
      def post(self,request):
          _data= request.data
          serializer= RegisterSerializer(data=_data)
          
          if not serializer.is_valid():
              return Response({'message':serializer.errors},status=status.HTTP_404_NOT_FOUND)
           
          serializer.save()
          return Response({'message':'user created'},status=status.HTTP_201_CREATED)

class LoginAPI(APIView):
    permission_classes=[AllowAny]

    def post(self,request):
        _data = request.data
        serializer = LoginSerializers(data=_data)
        
        if not serializer.is_valid():
            return Response({'message':'invalid credentals'},status=status.HTTP_404_NOT_FOUND)
        
        user = authenticate(username=serializer.data['username'],password=serializer.data['password'])
        
        if not user :
            return Response({"message": "Invalid username or password"}, status=400)
        
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
        'message': 'Login successful',
        'token': str(token),
        'username': user.username   # <--- Add this
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
        quantity = int(request.data.get("quantity", 1))

        cart, _ = Cart.objects.get_or_create(user=request.user)
        product = Product.objects.get(id=product_id)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity
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

        cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        cart_item.quantity = quantity
        cart_item.save()

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data)
    
#checkout
class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all()

        if not cart_items:
            return Response({"error": "Cart is empty"}, status=400)

        # Collect customer details
        house_name = request.data.get("house_name")
        place = request.data.get("place")
        pincode = request.data.get("pincode")
        mobile_number = request.data.get("mobile_number")

        if not all([house_name, place, pincode, mobile_number]):
            return Response({"error": "All address fields are required"}, status=400)

        # Calculate subtotal
        subtotal = sum(item.get_total_price() for item in cart_items)

        # Delivery charge logic
        if subtotal <= 1000:
            delivery_charge = 80
        elif subtotal <= 2000:
            delivery_charge = 160
        elif subtotal <= 3000:
            delivery_charge = 220
        else:
            delivery_charge = 0

        total = subtotal + delivery_charge

        order = Order.objects.create(
            user=request.user,
            total_price=total,
            house_name=house_name,
            place=place,
            pincode=pincode,
            mobile_number=mobile_number,
            is_paid=False
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        cart_items.delete()  # clear cart after checkout

        return Response({
            "message": "Order created",
            "order_id": order.id,
            "subtotal": subtotal,
            "delivery_charge": delivery_charge,
            "total": total
        })
  
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_list_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)