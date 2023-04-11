from django.contrib import admin
from .models import Category,Product,Variant,Size
# Register your models here.

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Variant)
admin.site.register(Size)

