from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100,unique=True)

    def __str__(self):
        return self.name

class Quality(models.Model):
    name = models.CharField(max_length=100,unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    quality = models.ForeignKey(
    Quality,
    on_delete=models.CASCADE,
    null=True,
    blank=True
)

    def __str__(self):
        return self.name
    


class ProductMedia(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="media")
    file = models.FileField(upload_to="product_media/")
    media_type = models.CharField(
        max_length=10,
        choices=(("image", "Image"), ("video", "Video")),
    )

    def __str__(self):
        return f"{self.product.name} - {self.media_type}"

class Colour(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Size(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    colour = models.ForeignKey(Colour, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    stock = models.PositiveIntegerField()

    class Meta:
        unique_together = ('product', 'colour', 'size')

    def __str__(self):
        return f"{self.product.name} - {self.colour.name} - {self.size.name} ({self.stock})"


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    colour = models.ForeignKey(Colour, on_delete=models.CASCADE, null=True, blank=True)
    size = models.ForeignKey(Size, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        if self.colour and self.size:
            return f"{self.quantity} × {self.product.name} ({self.colour.name}, {self.size.name})"
        return f"{self.quantity} × {self.product.name}"

    def get_total_price(self):
        return self.quantity * self.product.price


    #checkout and order


class Order(models.Model):

    STATUS_CHOICES = [
        ("PLACED", "Placed"),
        ("PACKED", "Packed"),
        ("SHIPPED", "Shipped"),
        ("DELIVERED", "Delivered"),
        ("CANCELLED", "Cancelled"),
        ("RETURNED", "Returned"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)  # order time
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PLACED"
    )

    is_paid = models.BooleanField(default=False)

    # Customer details
    customer_name = models.CharField(max_length=255, null=True, blank=True)
    house_name = models.CharField(max_length=255)
    place = models.CharField(max_length=255)
    pincode = models.CharField(max_length=10)
    mobile_number = models.CharField(max_length=15)

    # Extra timestamps
    cancelled_at = models.DateTimeField(null=True, blank=True)
    packed_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Order {self.id} - {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    colour = models.ForeignKey(Colour, on_delete=models.CASCADE, null=True, blank=True)
    size = models.ForeignKey(Size, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        colour = self.colour.name if self.colour else "N/A"
        size = self.size.name if self.size else "N/A"
        return f"{self.product.name} ({colour}, {size}) × {self.quantity}"
