import re, json
from rest_framework import serializers
from .models import (
    Colour, Order, OrderItem, Product, Category, ProductMedia,
    ProductVariant, Quality, Cart, CartItem, Size,HomeImage,HomeVideo
)
from django.contrib.auth.models import User

class HomeImageSerializer(serializers.ModelSerializer):
    class Meta:   
        model = HomeImage
        fields = ['id', 'image', 'mobile_image']

class HomeVideoSerializer(serializers.ModelSerializer):
    class Meta:   
        model = HomeVideo
        fields = ['id', 'video', 'mobile_video']



# ---------------- CATEGORY & QUALITY ----------------

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

    def validate_name(self, value):
        if Category.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("Category with this name already exists.")
        return value


class QualitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Quality
        fields = ['id', 'name']

    def validate_name(self, value):
        if Quality.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("Quality with this name already exists.")
        return value


class ColourSerializer(serializers.ModelSerializer):
    class Meta:
        model = Colour
        fields = ["id", "name"]


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ["id", "name"]


# ---------------- PRODUCT VARIANTS ----------------

class ProductVariantSerializer(serializers.ModelSerializer):
    colour = ColourSerializer(read_only=True)
    size = SizeSerializer(read_only=True)

    colour_id = serializers.PrimaryKeyRelatedField(
        queryset=Colour.objects.all(), source="colour", write_only=True
    )
    size_id = serializers.PrimaryKeyRelatedField(
        queryset=Size.objects.all(), source="size", write_only=True
    )

    class Meta:
        model = ProductVariant
        fields = ["id", "product", "colour", "colour_id", "size", "size_id", "stock"]


# ---------------- PRODUCT MEDIA ----------------

class ProductMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMedia
        fields = ["id", "product", "file", "media_type"]



# ---------------- PRODUCT ----------------

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    quality = QualitySerializer(read_only=True)

    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source="category", write_only=True
    )
    quality_id = serializers.PrimaryKeyRelatedField(
        queryset=Quality.objects.all(), source="quality", write_only=True
    )

    variants = ProductVariantSerializer(many=True, required=False)
    media = ProductMediaSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = "__all__"

    def create(self, validated_data):
        request = self.context.get("request")
        variants_raw = request.data.get("variants") if request else None
        variants_data = json.loads(variants_raw) if variants_raw else []

        product = Product.objects.create(
            name=validated_data.get("name"),
            description=validated_data.get("description"),
            price=validated_data.get("price"),
            category=validated_data.get("category"),
            quality=validated_data.get("quality"),
        )

        for variant_data in variants_data:
            ProductVariant.objects.create(
                product=product,
                colour_id=variant_data["colour_id"],
                size_id=variant_data["size_id"],
                stock=variant_data["stock"],
            )

        if request:
            files = request.FILES.getlist("media")
            for file in files:
                media_type = "video" if file.content_type.startswith("video") else "image"
                ProductMedia.objects.create(
                    product=product,
                    file=file,
                    media_type=media_type,
                )

        return product


# ---------------- AUTH ----------------

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password2': "Passwords do not match"})

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
        validated_data.pop('password2')
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class LoginSerializers(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


# ---------------- CART ----------------

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")
    product_price = serializers.ReadOnlyField(source="product.price")
    colour = ColourSerializer(read_only=True)
    size = SizeSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            "id", "product", "product_name", "product_price",
            "colour", "size", "quantity", "total_price", "product_image"
        ]

    def get_total_price(self, obj):
        return obj.get_total_price()

    def get_product_image(self, obj):
        media = obj.product.media.filter(media_type="image").first()
        return media.file.url if media else None



class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_cart_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "user", "created_at", "items", "total_cart_price"]
        read_only_fields = ["user"]

    def get_total_cart_price(self, obj):
        return sum(item.get_total_price() for item in obj.items.all())


# ---------------- ORDER ----------------

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")
    colour = ColourSerializer(read_only=True)
    size = SizeSerializer(read_only=True)
    product_image = serializers.SerializerMethodField()
    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "colour", "size", "quantity", "price", "product_image"]

    def get_product_image(self, obj):
        media = obj.product.media.filter(media_type="image").first()
        return media.file.url if media else None

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "user", "created_at", "total_price", "is_paid","customer_name",
            "house_name", "place", "pincode", "mobile_number", "items","status",
        ]
        read_only_fields = ["user", "total_price", "is_paid"]


# ---------------- USER PROFILE ----------------

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "date_joined"]
        read_only_fields = ["id", "date_joined"]


class ProfileUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ["username", "email", "password", "password2"]

    def validate_username(self, value):
        user = self.instance
        if User.objects.exclude(pk=user.pk).filter(username__iexact=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def validate_email(self, value):
        user = self.instance
        if User.objects.exclude(pk=user.pk).filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate(self, data):
        password = data.get("password")
        password2 = data.get("password2")

        if password or password2:
            if not password or not password2:
                raise serializers.ValidationError({"password2": "Both password fields are required"})

            if password != password2:
                raise serializers.ValidationError({"password2": "Passwords do not match"})

            errors = []
            if len(password) < 8 or len(password) > 20:
                errors.append("Password must be 8-20 characters long")
            if not re.search(r"\d", password):
                errors.append("Password must include at least one number")
            if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
                errors.append("Password must include at least one special character")
            if password.lower() == self.instance.username.lower():
                errors.append("Password cannot be same as username")

            if errors:
                raise serializers.ValidationError({"password": errors})

        return data

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        validated_data.pop("password2", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance
