import re
from rest_framework import serializers
from .models import Order, OrderItem, Product, Category, Quality,Cart, CartItem
from django.contrib.auth.models import User
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class QualitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Quality
        fields = ['id', 'name']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    quality = QualitySerializer()

    class Meta:
        model = Product
        fields = '__all__'

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, style={'input_type': 'password'})  # Confirm password

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate(self, data):
        # Password confirmation
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password2': "Passwords do not match"})

        # Collect password errors
        password_errors = []

        if len(data['password']) < 8 or len(data['password']) > 20:
            password_errors.append("Password must be 8-20 characters long")
        if not re.search(r'\d', data['password']):
            password_errors.append("Password must include at least one number")
        if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', data['password']):
            password_errors.append("Password must include at least one special character")
        if data['password'].lower() == data['username'].lower():
            password_errors.append("Password cannot be same as username")

        if password_errors:
            raise serializers.ValidationError({'password': password_errors})

        return data

    def create(self, validated_data):
        validated_data.pop('password2')  # remove confirm password
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
# authentication login and register

class LoginSerializers(serializers.Serializer):
      username= serializers.CharField()
      password= serializers.CharField()

# serializers.py

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")
    product_price = serializers.ReadOnlyField(source="product.price")
    product_image = serializers.ImageField(source="product.image", read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_name", "product_image", "product_price", "quantity", "total_price"]

    def get_total_price(self, obj):
        return obj.get_total_price()


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_cart_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "user", "created_at", "items", "total_cart_price"]
        read_only_fields = ["user"]

    def get_total_cart_price(self, obj):
        return sum(item.get_total_price() for item in obj.items.all())

#order and checkout

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")
    product_image = serializers.ImageField(source="product.image", read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "quantity", "price","product_image"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    

    class Meta:
        model = Order
        fields = ["id", "user", "created_at", "total_price", "is_paid",
                  "house_name", "place", "pincode", "mobile_number", "items"]
        read_only_fields = ["user", "total_price", "is_paid"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "date_joined"]  
        read_only_fields = ["id", "date_joined"]     