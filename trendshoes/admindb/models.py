from django.db import models
from accounts.models import User


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    updated = models.DateField(auto_now=True)
    created = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Variant(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color = models.CharField(max_length=100, unique=True)
    # name = models.ForeignKey(Color, on_delete=models.CASCADE)
    price = models.PositiveBigIntegerField()
    dprice = models.PositiveBigIntegerField(null=True)
    img1 = models.ImageField(upload_to='uploads')
    img2 = models.ImageField(upload_to='uploads',null=True)
    img3 = models.ImageField(upload_to='uploads',null=True)
    available = models.BooleanField(default=True)
    updated = models.DateField(auto_now=True)
    created = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.product} ({self.color})"
    
class Size(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    size = models.CharField(max_length=100)
    stock = models.PositiveIntegerField(null=True)
    available = models.BooleanField(default=True)
    updated = models.DateField(auto_now=True)
    created = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.variant}) ({self.size})"
    
    def __str__(self):
        return self.size
    

