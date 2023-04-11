from django.db import models
from accounts.models import User
from django.core.validators import RegexValidator
from admindb.models import Variant,Size
# Create your models here.

STATE_CHOICES = (
    ('Kerala','Kerala'),
    ('Tamilnadu','Tamilnadu'),
    ('Karnataka','Karnataka'),
    ('AndraPradesh','AndraPradesh')
)
DIST_CHOICES = {
    ('Kannur','Kannur'),
    ('Kochi','Kochi'),
    ('Kozhikkode','Kozhikkode'),
    ('Ernakulam','Ernakulam'),
    ('Thiruvananthapuram','Thiruvananthapuram'),
    ('Banglore','Banglore'),
    ('Hubli','Hubli'),
    ('Hydrabad','Hydrabad'),
    ('Coimbator','Coimbator'),
    ('Madurai','Madurai'),
}

class UserProfile(models.Model):
    user=models.OneToOneField(User , on_delete=models.CASCADE, related_name='profile')
    is_verified=models.BooleanField(default=False)
    otp=models.CharField(max_length=6, null=True , blank=True)


    def _str_(self):
        return self.user.email

class users(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    password=models.CharField(max_length=50)
    def _str_(self):
        return self.email

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    firstname = models.CharField(max_length=100,null=True)
    lastname = models.CharField(max_length=100,null=True)
    email = models.EmailField(max_length=200)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    phone_regex = RegexValidator(regex=r'^\d+$', message="Mobile number should only contain digits")
    phone = models.CharField(validators=[phone_regex], max_length=10, null=True)
    city = models.CharField(choices=DIST_CHOICES,max_length=255)
    state = models.CharField(choices=STATE_CHOICES,max_length=255)
    pincode_regex = RegexValidator(regex=r'^\d+$', message="Pincode should only contain digits")
    pincode = models.PositiveIntegerField(null=True,blank=True)

    def _str_(self):
        return self.user.username
    
class wishlist(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Variant,on_delete=models.CASCADE)

    def str(self):
        return self.product.product

class CartItem(models.Model):
    product = models.ForeignKey(Variant, on_delete=models.CASCADE)
    # size = models.ForeignKey(Size, on_delete=models.CASCADE)
    size = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def str(self):
        return f"{self.quantity} x {self.product}"
    
    def sub_total(self):
        return self.product.price * self.quantity
    
class Payment(models.Model):
    customer = models.ForeignKey(User,on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=30)
    refund_id = models.CharField(max_length=30)
    order_id = models.CharField(max_length=100,blank=True,default='empty')
    payment_method = models.CharField(max_length=100)
    amount_paid = models.FloatField(default=0)
    paid = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.payment_id
    
class Order(models.Model):
    STATUS = (
        ('Order Confirmed', 'Order Confirmed'),
        ('Shipped',"Shipped"),
        ('Out for delivery',"Out for delivery"),
        ('Delivered', 'Delivered'),
        ('Cancelled','Cancelled'),
        ('Returned','Returned'),
    )
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    order_number = models.CharField(max_length=50)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    order_total = models.FloatField()
    order_discount = models.FloatField(default=0)
    paid_amount = models.FloatField()
    # tax = models.FloatField()
    payment = models.ForeignKey(Payment,on_delete=models.SET_NULL,blank=True,null=True)
    status = models.CharField(max_length=50,choices=STATUS,default='Order Confirmed')
    ip = models.CharField(blank=True,max_length=50)
    is_ordered = models.BooleanField(default=False)
    is_returned = models.BooleanField(default=False)
    return_reason = models.CharField(max_length=50, blank=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    refund_completed = models.BooleanField(default=False)
    def __str__(self):
        return self.order_number



class OrderProduct(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE,related_name='user_order_page')
    customer = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Variant,on_delete=models.CASCADE)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return self.product.name
    def sub_total(self):
        return self.product.price * self.quantity
    
class ProductReview(models.Model):
    RATINGS = (
        ('Poor', 'Poor'),
        ('Fair', 'Fair'),
        ('Average', 'Average'),
        ('Good', 'Good'),
        ('Excellent', 'Excellent'),
    )
    user = models.CharField(max_length=50)
    product = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name='reviews')
    rating = models.CharField(max_length=50,choices=RATINGS,default='Average')
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.product.product.name} ({self.rating})'

    class Meta:
        ordering = ['-created_at']