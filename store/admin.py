from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from . models import *

# Register your models here.

# class UserAdmin(admin.ModelAdmin):
#     list_display = ['id', 'username', 'first_name', 'last_name']
# admin.site.register(User, UserAdmin)

# class UserAdmin(admin.ModelAdmin):
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2","first_name", "last_name"),
            },
        ),
    )
    # list_display = ['id', 'username', 'first_name', 'last_name']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'title']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id','title', 'slug', 'price', 'description', 'junk', 'when_uploaded', 'last_updated', 'category']

