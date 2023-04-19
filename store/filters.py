import django_filters
from dataclasses import fields
from django_filters.rest_framework import FilterSet
from .models import Product

class ProductFilter(FilterSet):
    description = django_filters.LookupChoiceFilter(field_name='description')
    class Meta:
        model = Product
        fields = {
            'category_id': ['exact'],
            'price': ['gt', 'lt']
        }