from django.urls import path
from .  views import *

urlpatterns = [
    path('admindashboard/', admindashboard, name="admindashboard"),
    path('adminlogin/', adminlogin, name="adminlogin"),
    path('adminlogout/', adminlogout, name="adminlogout"),
    path('viewcategory/', viewcategory, name="viewcategory"),
    path('addcategory/', addcategory, name="addcategory"),
    path('deletecategory/<int:id>/', deletecategory, name="deletecategory"),
    path('searchcategory/', searchcategory, name="searchcategory"),
    path('viewproduct/', viewproduct, name="viewproduct"),
    path('searchproduct/', searchproduct, name="searchproduct"),
    path('editproduct/<int:id>/', editproduct, name="editproduct"),
    path('productdetails/<int:id>/', productdetails, name="productdetails"),
    path('addproduct/', addproduct, name="addproduct"),
    path('deleteproduct/<int:id>/', deleteproduct, name="deleteproduct"),
    path('viewvariant/', viewvariant, name="viewvariant"),
    path('searchvariant/', searchvariant, name="searchvariant"),
    path('addvariant/<int:id>/', addvariant, name="addvariant"),
    path('deletevariant/<int:id>/', deletevariant, name="deletevariant"),
    path('addsizeandstock/<int:id>/', addsizeandstock, name="addsizeandstock"),
    path('deletesize/<int:id>/', deletesize, name="deletesize"),
    path('editvariant/<int:id>/', editvariant, name="editvariant"),
    path('viewuser/', viewuser, name="viewuser"),
    path('searchuser/', searchuser, name="searchuser"),
    path('blockuser/<int:id>/', blockuser, name="blockuser"),
    path('manage_order/', manage_order, name="manage_order"),
    path('orderdetails/<int:id>/', orderdetails, name="orderdetails"),
    path('searchorder/', searchorder, name="searchorder"),
    path('update_order/<int:id>/', update_order, name="update_order"),
    path('admincancelOrder/<int:id>/',admincancelOrder, name='admincancelOrder'),

]