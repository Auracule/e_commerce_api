from django.db import models
from django.core.validators import MinValueValidator, FileExtensionValidator
from django.contrib.auth.models import AbstractUser
from uuid import uuid4
from . validators import validate_file_size


# Create your models here.
class User(AbstractUser):
    email = models.EmailField(unique=True)
    post_active_score = models.IntegerField(null=True, blank=True)


class Customer(models.Model):
    Gold = 'G'
    Silver = 'S'
    Bronze = 'B'

    MEMBERSHIP_OPTIONS = [
        # ('actual db', 'dropfown text')
        (Gold, 'Gold'),
        (Silver, 'Silver'),
        (Bronze, 'Bronze'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    mobile = models.CharField(max_length=30)
    birth_date = models.DateField(null=True)
    membership = models.CharField(max_length=50, choices=MEMBERSHIP_OPTIONS, default=Silver)

    class Meta:
        ordering = ['user__first_name', 'user__last_name']

    def __str__(self):
        return f'{self.user}'
    
        # indexes = [
        #     models.Index(fields=['first_name', 'last_name'])
        # ]


class Address(models.Model):
    CONTACT_OPTIONS = [
        ('res', 'residential'),
        ('work', 'work/corporate'),
    ]
    
    contact_type = models.CharField(max_length=200)
    street = models.CharField(max_length=200)
    city = models.CharField(max_length=70)
    state = models.CharField(max_length=20)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

class Category(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title
    
class Promotion(models.Model):
    title = models.CharField(max_length=200)

    # def __str__(self):
    #     return self.title
    
class Product(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(default='-')
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField()
    junk = models.CharField(max_length=250, null=True, blank=True, default='')
    when_uploaded = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    promotions = models.ManyToManyField(Promotion)

    def __str__(self):
        # return f'{self.title} - {self.category.title}'
        return self.title

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='image')
    image = models.ImageField(upload_to='store/image', default='prodefault.jpg', validators = 
    [validate_file_size, FileExtensionValidator(allowed_extensions=['png', 'jpeg'])])


class Order(models.Model):
    PAYMENT_STATUS = [
        ('pending', 'PENDING'),
        ('completed', 'COMPLETED'),
        ('failed', 'FAILED'),
    ]

    DELIVERY_STATUS = [
        ('pending', 'PENDING'),
        ('completed', 'COMPLETED'),
        ('failed', 'FAILED'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING)
    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=50, default='pending', choices= PAYMENT_STATUS)
    delivery_status = models.CharField(max_length=50, default='pending', choices= DELIVERY_STATUS)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    quantity = models.PositiveSmallIntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2)


# class Cart(models.Model):
#     placed_at = models.DateTimeField(auto_now_add=False)


class Cart(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True)  # This is for the a unique id for the products added to the cart. This is to prevent your cart from external sources (other users).
    placed_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    quantity = models.PositiveSmallIntegerField()
    # quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        unique_together = [['cart', 'product']]  # This ensures that similar items added to the cart don't replicate but just increases in quantity.


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    reviewer_name = models.CharField(max_length=250)
    remark = models.TextField()
    posted_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'Review for {self.product.title}'




    
