from django.contrib import admin
from .models import UserProfile,wishlist,Address,CartItem,ProductReview,Order

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Address)
admin.site.register(CartItem)
admin.site.register(wishlist)
admin.site.register(ProductReview)
admin.site.register(Order)
