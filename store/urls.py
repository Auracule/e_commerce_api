# from unicodedata import lookup
from django.urls import path, include
from rest_framework.routers import SimpleRouter, DefaultRouter  # This for the viewset models in the views
from rest_framework_nested import routers  # This is for the nested routers
from store.models import Product
# from pprint import pprint

from . import views


# This is for the nested routers
router = routers.DefaultRouter()
router.register('products', views.ProductViewSet, basename='products')
router.register('carts', views.CartViewSet, basename='carts')
router.register('customers', views.CustomerViewSet, basename='customers')
router.register('orders', views.OrderViewSet, basename='orders')

# product to review nested routing
products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')  # This registers the url as a nested router
products_router.register('reviews', views.ReviewViewSet, basename='product-reviews')# This allows configuration of the already created nested url
products_router.register('images', views.ProductImageViewSet, basename='product-images')# This allows configuration of the already created nested url

cart_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')  # This registers the url as a nested router
cart_router.register('items', views.CartItemViewSet, basename='cart-items')# This allows configuration of the already created nested url


# This for the normal viewset
# router = SimpleRouter()
# router.register('products', views.ProductViewSet, basename='products')  # the prefix 'products' is what displays as a url

# router = DefaultRouter()
# router.register('products', views.ProductViewSet, basename='products')


# This is a the url pattern for the nestedviewset(its optional)
# urlpatterns = router.urls + products_router.urls

urlpatterns = [
    ## THIS IS FOR ROUTER
    path('', include(router.urls)),
    path('', include(products_router.urls)),
    path('', include(cart_router.urls)),

    ### THIS IS FOR THE CLASS BASED VIEWS
    # path('products/', views.ProductList.as_view()),  # ".as_views()" generates function url for the CBV
    # path('products/<int:pk>/', views.ProductDetail.as_view()),
    path('category/', views.CategoryList.as_view()),
    # path('category/', views.category_list),
    path('category/<int:pk>/', views.CategoryDetail.as_view()),

    ### THIS IS FOR THE FUNCTION BASED VIEWS
    # path('products/', views.product_list),
    # path('products/<int:pk>/', views.product_detail),
    # path('categories/', views.category_list),
    # path('categories/<int:pk>/', views.category_detail),
    # path('categories/<int:pk>/', views.category_detail, name='category-detail'), # This is for the HyperlinkedRelatedField 
]
