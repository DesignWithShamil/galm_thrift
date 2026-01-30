from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer

@api_view(['GET'])
def product_list(request):
    products = Product.objects.select_related('category','quality').all()  # optimized query
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)  # make sure this is DRF Response


@api_view(['GET'])
def category_list(request):
    categories = Category.objects.prefetch_related('product_set').all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)
