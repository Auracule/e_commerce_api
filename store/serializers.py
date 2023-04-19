from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from . models import Product, Category, Review, Cart, CartItem, Customer, Order, OrderItem, ProductImage
from rest_framework.validators import ValidationError
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer



# class CategorySerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     title = serializers.CharField(max_length=200)

class CategorySerializer(serializers.ModelSerializer):
    product_count  = serializers.IntegerField(read_only=True)  # We added this field manually into the Category, Since its not of much importance. The read_only makes the product unable to participate in POST, UPDATE or CREATE operaions. But it will just dispalyed when you list out categories
    class Meta:
        model = Category
        fields = ['id', 'title', 'product_count']



# class ProductSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     title = serializers.CharField()
#     price = serializers.DecimalField(max_digits=6, decimal_places=2)
#     unit_price = serializers.DecimalField(max_digits=6, decimal_places=2, source='price')
#     # creating a field that isn't in our model using teh serializermethodfield: This is used for calculating a function using a field from the model
#     product_tax = serializers.SerializerMethodField(method_name='calc_tax') 
#     # category = serializers.PrimaryKeyRelatedField(queryset = Category.objects.all()) # This is to display the id of the category of each product
#     # category = serializers.StringRelatedField() # This is used to display the category title and not id. But you have to define a "def __str__(self): return self.title" function in the category model
#     # category = CategorySerializer() # This is to display both id and title as a dictionary
#     category = serializers.HyperlinkedRelatedField(queryset = Category.objects.all(), view_name='category-detail') # This is to create a hyperlink instead of a dictionary

#     # This is a function built to calculate the tax for the product
#     def calc_tax(self, prod): # The parameter 'prod', represents the instance of the product model you are calling.
#         return prod.price * Decimal(0.45)

class ProductImageSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        myid = self.context['prod_id']
        return ProductImage.objects.create(product_id=myid, **validated_data)

    class Meta:
        model = ProductImage
        fields = ['id','image']


class ProductSerializer(serializers.ModelSerializer):
    image = ProductImageSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = ['id', 'title', 'description','price', 'category', 'product_tax', 'image']
        # fields = '__all__' This shows all the fields present in the model
        # fields = ['id', 'title', 'description', 'unit_price', 'category', 'product_tax'] # This is when you want to change the unit price

    # This is a custom Validation
    def validate(self, data):
        if data['price'] < 5000:
            raise ValidationError('Invalid Price! Price cannot be less than 5000')
        return data

    # CREATE & UPDATE CUSTOM METHOD
    def create(self, validated_data):
        prod = Product(**validated_data)  # <== '**' this unpacks the validate_data
        prod.junk = 'This is some crap I created'  #  OR
        prod.junk = f'{prod.title} - This is my crap'
        prod.save()
        return prod

    # This is the update
    def update(self, prod, validated_data):
        prod.title = validated_data.get('title', prod.title)
        prod.price = validated_data.get('price', prod.price)
        prod.when_uploaded = validated_data.get('when_uploaded', prod.when_uploaded)
        prod.last_updated = validated_data.get('last_updated', prod.last_updated)
        prod.category = validated_data.get('category', prod.category)
        prod.description = ' ------ "Endorsed"'
        prod.save()
        return prod

    price = serializers.DecimalField(max_digits=6, decimal_places=2)
    # unit_price = serializers.DecimalField(max_digits=6, decimal_places=2, source='price')  # This is to customise the model field
    product_tax = serializers.SerializerMethodField(method_name='calc_tax')
    def calc_tax(self, prod):
        return prod.price * Decimal(0.45)

        
class SimpleProductSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    class Meta:
        model = Product
        fields = ['id', 'title', 'price', 'category']


class ReviewSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = Review
        fields = ['id', 'posted_at', 'reviewer_name', 'remark', 'product']


class CartItemSerializer(serializers.ModelSerializer):
    # id = serializers.UUIDField(read_only=True)
    product = SimpleProductSerializer()
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'sub_ ']
    
    sub_total = serializers.SerializerMethodField()

    def get_sub_total(self, item:CartItem):
        return item.quantity * item.product.price

# class AddCartItemSerializer(serializers.ModelSerializer):
#     product_id = serializers.IntegerField()

#     class Meta:
#         model = CartItem
#         fields = ['id','product_id', 'quantity']

#     def save(self, **kwargs):
#         product_id = self.validated_data['product_id']
#         quantity = self.validated_data['quantity']
#         cart_id = self.context['cart_id']

#         return super().save(**kwargs)


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()
    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('Sorry bros the items youa re trying to fetch is not in the DB')
        return value
    
    # def validate_quantity(self, value):
    #     if quantity < 1:
    #         raise serializer.ValidationError('Sorry cannot add item less than 1')
    #     return value
        
    def save(self, **kwargs):
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        cart_id = self.context['cart_id']

        cartitem = CartItem.objects.filter(product_id=product_id, cart_id=cart_id).first()
        if cartitem:
            cartitem.quantity += quantity
            cartitem.save()
            self.instance = cartitem
        else:
            # self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)
            newitem = CartItem.objects.create(cart_id=cart_id, **self.validated_data)
            self.instance = newitem
        return self.instance

        

class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)  # to show nothing in the raw in the browseable API
    items = CartItemSerializer(source='cartitem_set', many=True, read_only=True)
    grand_total = serializers.SerializerMethodField()

    def get_grand_total(self, cart:Cart):
        return sum([item.quantity * item.product.price for item in cart.cartitem_set.all()])

    class Meta:
        model = Cart
        fields = ['id', 'items', 'grand_total']


    # many=True when you want to list 

class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']

# class AddItemCartSerializer(serializers.ModelSerializer):
#     id = serializers.UUIDField(read_only=True)
#     class Meat:
#         models = CartItem
#         fields = ['id', 'product_id', 'quantity']

#     def save(self, **kwargs):
#         product_id = self.validated_data['product_id']
#         quantity = self.validated_data['quantity']

#         cart_id = self.context['cart_id']
#         cartitem = Cart.objects.filter(product_id=product_id, cart_id=cart_id).first()
#         if cartitem:
#             cartitem.quantity += quantity
#             cartitem.save()
#             self.instance = cartitem
#         else:
#             # self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)
#             newitem = CartItem.objects.create(cart_id=cart_id, **self.validated_data)
#             self.instance = newitem
#         return self.instance


class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id', 'username', 'email','password', 'first_name', 'last_name']


class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True) 
    class Meta:
        model = Customer
        fields = ['id', 'user_id', 'birth_date', 'membership']

class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'price', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True, source='orderitem_set')
    class Meta:
        model = Order
        fields = ['id', 'items', 'customer','placed_at', 'payment_status', 'delivery_status']

class CreateOrderSerializer(serializers.Serializer): 
    cart_id = serializers.UUIDField()
    
    def validate_cart_id(self, cartid):
        if not Cart.objects.filter(id=cartid).exists():
            raise serializers.ValidationError('Invalid cart is supplied')
        # return Cart.objects.filter(id=cartid)

        # if CartItem.objects.filter(cart_id=cartid).exists() == 0
        if not CartItem.objects.filter(cart_id=cartid).exists():
            raise serializers.ValidationError('Your cart is empty')
        return cartid

    # @transaction.atomic()
    def save(self, **kwargs):
        with transaction.atomic():
            # print("CARTID >>>>",self.validated_data['cart_id'])
            # print("User ID >>>>",self.context['userid'])
            cart_id = self.validated_data['cart_id']
            user_id = self.context['user_id']

            # return 
            # 1 creating the order
            # (customer, created)=Customer.objects.get_or_create(user_id=user_id)
            # (customer, created)=Customer.objects.get_or_create(user_id=user_id)
            customer =Customer.objects.get(user_id=user_id)
            theorder = Order.objects.create(customer=customer, delivery_status='pending')
            
            # 2 copying the cartitem to create the order item
            cartitems = CartItem.objects.filter(cart_id=cart_id)

            orderitems = [OrderItem
                (order=theorder,
                product=items.product, 
                quantity=items.quantity, 
                price=items.product.price) for items in cartitems
            ]
            OrderItem.objects.bulk_create(orderitems)
            
            # 3 Deleting the cart
            # thecart = Cart.objects.filter(id=cart_id).exists():
            thecart = Cart.objects.get(id=cart_id)
            if thecart:
                thecart.delete()    
            return theorder    

            
class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status', 'delivery_status']