from rest_framework import serializers
from .models import Product, Category, Quality

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
