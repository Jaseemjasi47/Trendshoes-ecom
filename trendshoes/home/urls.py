from django.urls import path
from .  views import *

urlpatterns = [
    path('', index,name="index"),
    path('signup/', signup, name="signup"), 
    path('login/', login_user, name="login"),
    path('logout/', logout, name="logout"),
    path('verifyotp/<int:user_id>/', verifyotp, name="verifyotp"),
    path('resendotp/<int:user_id>/', resendotp, name="resendotp"),
    path('forgotpassword/', forgotpassword, name="forgotpassword"),
    path('repassword/<int:user_id>/', repassword, name="repassword"),
    path('userprofile/<int:id>/', userprofile, name="userprofile"),
    path('addaddress/<int:id>/', add_address, name="addaddress"),
    path('editprofile/<int:id>/', editprofile, name="editprofile"),
    path('deladdress/<int:id>/', deladdress, name="deladdress"),
    path('changepassword/', changepassword, name="changepassword"),
    path('category/<int:cid>/', category, name="category"),
    path('product/<int:id>/',singleproduct,name='singleproduct'),
    path('search/', search, name="search"),
    path('contact/', contact, name="contact"),
    path('wishlist/', userwishlist, name="wishlist"),
    path('addwishlist/<int:product_id>/',add_to_wishlist,name='add_to_wishlist'),
    path('removewishlist/<int:product_id>/',remove_from_wishlist,name='remove_from_wishlist'),
    path('viewcart/', viewcart, name="viewcart"),
    path('addtocart/<int:variant_id>/', addtocart, name='addtocart'),
    path('removecartproduct/<int:product_id>/', removecartproduct,name='removecartproduct'),
    path('addcartitem/<int:product_id>/', addcartitem,name='addcartitem'),
    path('removecartitem/<int:product_id>/', removecartitem,name='removecartitem'),
    path('checkout/', checkout, name="checkout"),
    path('myorder/', myorders, name="myorders"),
    path('confirmation/<int:id>/', confirmation, name="confirmation"),
    path('proceed_to_pay/',razorPayCheck,name='razorpaycheck'), 
    path('placeorder/', placeOrder, name='place_order'),
    path('ordercomplete/<str:ordernumber>/',orderComplete, name='order_complete'),
    path('vieworder/<int:id>/',viewOrder, name='vieworder'),
    path('cancelOrder/',cancelOrder, name='cancelOrder'),
    # path('addproductreview/<int:order_product_id>/', addproductreview,name='addproductreview'),
    path('addreview/', addreview,name='addreview'),
    

]