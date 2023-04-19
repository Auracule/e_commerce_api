from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from rest_framework.decorators import api_view  # import the method that will be kept above every view instance
from rest_framework.response import Response  # This allows us to replace 'render & HttpResponse' with 'Response'
from rest_framework.views import APIView # This is for the class based views
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView  # This is for the concrete mixin class
from rest_framework.viewsets import ModelViewSet, GenericViewSet  # This is for the viewset class
from django_filters.rest_framework import DjangoFilterBackend # This is for the django_filters
from .filters import ProductFilter # This is from the filter  generic filtering
from rest_framework.filters import SearchFilter  # This is for the search  generic filtering
from rest_framework.filters import SearchFilter, OrderingFilter  # This is the sorting generic filtering
from rest_framework.pagination import PageNumberPagination  # This is for pagination
from .pagination import DefaultPagination, ProductPagination  # This is for custom pagination
from rest_framework import status  # This is for the HTTP status code 
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin
from rest_framework.validators import ValidationError  # This is to raise a validation error
from .models import Category, Product, Promotion, Review, Cart, CartItem, Customer, Order, OrderItem
from .serializers import *
# from .serializers import CategorySerializer, ProductSerializer, ReviewSerializer, CartSerializer, CartItemSerializer, AddCartItemSerializer
from store import serializers
from django.db.models import Count, Value  # This is for the annotation 
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny, IsAuthenticatedOrReadOnly, DjangoModelPermissions
from rest_framework.decorators import action
from . permissions import IsAdminOrReadOnly, FullDjangoModelPermissions
#type:ignore


# Create your views here.

# Using viewset
class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_fields = ['category_id', 'price']  # This is just with the normal filter which uses equals to
    filterset_class = ProductFilter  # This is when you have added from the filter file
    # This is for the search filter
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'when_uploaded'] 
    pagination_class = PageNumberPagination 
    pagination_class = ProductPagination
    # permission_classes = [IsAdminUser]
    # permission_classes = [IsAuthenticated]
    # permission_classes = [IsAuthenticated, IsAdminUser]
    # permission_classes = [AllowAny]
    # permission_classes = [IsAdminOrReadOnly]
    # permission_classes = [DjangoModelPermissions]
    permission_classes = [FullDjangoModelPermissions]

    

    
    def get_queryset(self):
        # Product.objects.all()
        #filtering in viewset
        queryset = Product.objects.all()
        cat_id = self.request.query_params.get('category_id')   # type: ignore
        if cat_id:  #or if cat_id is not none:, They are the same
            queryset = Product.objects.filter(category_id=self.request.query_params.get('category_id'))     # type: ignore
        # return Product.objects.filter(category_id=)
        return queryset

    def destroy_queryset(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        if product.pk == 1:
            raise ValidationError("Sorry you can't delete this product")
        product.delete()
        return Response({'message': 'object deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

class ProductImageViewSet(ModelViewSet):
    serializer_class = ProductImageSerializer
    # queryset = ProductImage.objects.all()

    def get_serializer_context(self):
        return {'prod_id': self.kwargs['product_pk']}
        
    def get_queryset(self):
        return ProductImage.objects.filter(product_id = self.kwargs['product_pk'])

class CustomerViewSet(ModelViewSet):
# class CustomerViewSet(CreateModelMixin,RetrieveModelMixin,UpdateModelMixin,GenericViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    # permission_classes = [IsAdminUser]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticatedOrReadOnly()]
        return [IsAdminUser()]


    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
    def me(self, request):
        # (customer, created) = Customer.objects.get_or_create(user__id=request.user.id)
        customer = Customer.objects.get(user__id=request.user.id)
        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)




# Generic class using Mixins
# class ProductList(ListCreateAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer

#     def get_queryset(self):
#         return Product.objects.all()


# class ProductDetail(RetrieveUpdateDestroyAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer

#     def delete(self, request, pk):
#         product = get_object_or_404(Product, pk=pk)
#         if product.pk == 1:
#             raise ValidationError("Sorry you can't delete this product")
#         product.delete()
#         return Response({'message': 'object deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


# class ProductList(APIView):
#     def get(self, request):
#         productqs = Product.objects.all()
#         serializer = ProductSerializer(productqs, many=True, context={'request':request})
#         return Response(serializer.data)

#     def post(self, request):
#         serializer = ProductSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data,status=status.HTTP_201_CREATED)
#         else: 
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# class ProductDetail(APIView):
#     def get(self, request, pk):
#         product = get_object_or_404(Product, pk=pk)
#         serializer = ProductSerializer(product)
#         return Response(serializer.data)

#     def put(self, request, pk):
#         product = get_object_or_404(Product, pk=pk)
#         serializer = ProductSerializer(product, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     def delete(self, request, pk):
#         product = get_object_or_404(Product, pk=pk)
#         product.delete()
#         return Response({'message': 'object deleted successfully'}status=status.HTTP_204_NO_CONTENT)



# @api_view()  # Inside the @api_view() is a GET request by default, so we don't need to indicate it
# def product_list(request): # This is to list all the product 
#     productqs = Product.objects.all()
#     serializer = ProductSerializer(productqs, many=True, context={'request':request})  # Without this, the server will give us a error because serializer doesn't handle many request. Putting 'many=True' makes it possible & error free
#                                                                                        # The context is key in django. It helps supply additional info to the serializer. the use of this context here is in conjuction with the hyperlink field in the serializer
#     return Response(serializer.data)  # Data is a method so as to activate theserializer. It is compulsory and indisposable




# # A function for both GET and POST
# @api_view(['GET', 'POST'])
# def product_list(request):
#     if request.method == 'GET':
#         productqs = Product.objects.all()
#         serializer = ProductSerializer(productqs, many=True, context={'request':request})
#         return Response(serializer.data)
#     elif request.method == 'POST': # We deserialize POST requests so it is able to reach the database
#         serializer = ProductSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data,status=status.HTTP_201_CREATED)
#         else: 
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




# @api_view()
# def product_detail(request, pk):
#     # product = Product.objects.get(pk=pk)
#     product = get_object_or_404(Product, pk=pk)  # This simply mean, if the user inputs an id in the URL, which isn't in the database, it will will bring up a 404 error page
#     serializer = ProductSerializer(product)  # This is 
#     return Response(serializer.data)


# @api_view(['GET', 'POST', 'PUT', 'DELETE'])
# def product_detail(request, pk):
#     product = Product.objects.get(pk=pk)
#     if request.method == 'GET':
#         serializer = ProductSerializer(product)
#         return Response(serializer.data)
#     elif request.method == 'POST':
#         serializer = ProductSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#     elif request.method == 'PUT':
#         serializer = ProductSerializer(product, data=request.data)
#         serializer.is_valid(raise_exception=True)  # This is used instead of "if serializer.is_valid()..."
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     elif request.method == 'DELETE':
#         product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

class CategoryList(ListCreateAPIView):
    queryset = Category.objects.annotate(product_count=Count('product'))
    serializer_class = CategorySerializer

# @api_view()
# def category_list(request):
#     category = Category.objects.all()
#     serializer = CategorySerializer(category, many=True)
#     return Response(serializer.data)

class CategoryDetail(RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer   
         

# @api_view()
# def category_detail(request, pk):
#     # category = Category.objects.get(pk=pk)
#     category = get_object_or_404(Category, pk=pk)
#     serializer = CategorySerializer(category)   
#     return Response(serializer.data)



class ReviewViewSet(ModelViewSet):
    # queryset = Review.objects.filter(product_pk=pk)
    serializer_class = ReviewSerializer
    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk']).all()



class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Cart.objects.prefetch_related('cartitem_set__product').all()
    serializer_class = CartSerializer


class CartItemViewSet(ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete"]
    # serializer_class = CartItemSerializer
    def get_queryset(self):
        return CartItem.objects.select_related('product').filter(cart_id= self.kwargs['cart_pk'])
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_serializer_context(self):
        return {'cart_id':self.kwargs['cart_pk'],'myname':'folorunso'}


class OrderViewSet(ModelViewSet):
    http_method_names = ['post', 'get', 'patch', 'delete']
    # queryset = Order.objects.all()
    # serializer_class = OrderSerializer
    # permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data, context={'user_id': request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)


    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
        
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return OrderSerializer
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return CreateOrderSerializer


    # def get_serializer_class(self):
    #     if self.request.method in ['GET', 'PATCH', 'PUT']:
    #         return OrderSerializer
    #     return CreateOrderSerializer

    def get_serializer_context(self):
        return{
            'userid': self.request.user.id,
            'author_name': 'promise',
        }

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(customer__user_id= self.request.user.id)
    