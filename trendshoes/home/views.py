from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages 
from django.contrib.auth.models import auth
from django.utils.crypto import get_random_string
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Q
from django.conf import settings
import trendshoes.settings
from django.core.mail import send_mail
from accounts.models import User
from .models import *
from admindb.models import Category,Product,Variant,Size
import random
from razorpay.errors import BadRequestError,ServerError
import razorpay
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
import os


from django.http import JsonResponse
import datetime

# Create your views here.

def login_user(request):
    if request.method == 'POST': 
        # username =request.POST['username']
        email =request.POST['email'] 
        password = request.POST['password'] 
        user = auth.authenticate(email=email, password=password) 
        if user is not None and user.profile.is_verified == True:
            request.session['email']=email
            auth.login(request,user)
            return redirect(index) 
        else: 
            messages.info(request, 'Invalid Email or Password') 
            return redirect('login')  
    return render(request, 'login.html')

def signup(request):
    user = None
    if request.method == 'POST':
        # Get form data
        first_name = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['cpassword']
        if len(password) < 6:
            messages.info(request,'Password should be at least 6 characters long')
            return redirect(signup)
        else:
            # Check if password and confirm password match
            if User.objects.filter(email=email).exists():
                        messages.info(request,'email entered has an existing account please login to access!')
                        return redirect(signup)
            elif password != confirm_password:
                        messages.error(request, 'Passwords do not match')
                        return redirect(signup)
            
            else:

            # Generate OTP
                otp = get_random_string(length=6, allowed_chars='1234567890')
            
            # Save user details to database
                user = User.objects.create_user(username=first_name, password=password, email=email)
            
            # Send OTP to user email
                subject = 'OTP for account verification'
                message = f'Your OTP for account verification is {otp}'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [email,]
                send_mail(subject, message, email_from, recipient_list)


            # Create UserProfile object for the user
                UserProfile.objects.create(user=user)
                
            # Save OTP to database
                user.profile.otp = otp
                user.profile.save()
            
            # Redirect to OTP verification page
                return redirect('verifyotp', user.id)

    return render(request, 'signup.html')

def verifyotp(request, user_id):
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        otp = request.POST['otp']
        if user.profile.otp == otp:
            user.profile.is_verified = True
            user.profile.otp = ''
            user.profile.save()
            messages.success(request, 'Account has been verified')
            return redirect(login_user)
        else:
            messages.error(request, 'Invalid OTP')
            return redirect('verifyotp', user_id)

    return render(request, 'verifyotp.html', {'user': user})


def resendotp(request, user_id):
    user = User.objects.get(id=user_id)

    # Generate new OTP
    otp = get_random_string(length=6, allowed_chars='1234567890')

    # Send new OTP to user email
    subject = 'New OTP for account verification'
    message = f'Your new OTP for account verification is {otp}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email,]
    send_mail(subject, message, email_from, recipient_list)

    # Save new OTP to database
    user.profile.otp = otp
    user.profile.save()

    messages.success(request, 'New OTP has been sent to your email')
    return redirect('verifyotp', user_id)

def forgotpassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            otp = get_random_string(length=6, allowed_chars='1234567890')
            user.profile.otp = otp
            user.profile.save()
            subject = 'OTP for password reset'
            message = f'Your OTP for password reset is {otp}'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email,]
            send_mail(subject, message, email_from, recipient_list)
            return redirect('repassword', user.id)
        else:
            messages.error(request, 'Email does not exist')
            return redirect(forgotpassword)
    return render(request, 'forgotpassword.html')

def repassword(request, user_id):
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        otp = request.POST['otp']
        if user.profile.otp == otp:
            password = request.POST['password']
            confirm_password = request.POST['confirm_password']
            if len(password) < 6:
                messages.info(request,'Password should be at least 6 characters long')
                return redirect(repassword)
            else:
                if password == confirm_password:
                    user.set_password(password)
                    user.profile.otp = ''
                    user.profile.save()
                    user.save()
                    messages.success(request, 'Password reset successful. Please login.')
                    return redirect('login')
                else:
                    messages.error(request, 'Passwords do not match')
        else:
            messages.error(request, 'Invalid OTP')
    return render(request, 'repassword.html', {'user': user})

def userprofile(request,id):
    user = User.objects.get(pk=id)
    try:
        address = Address.objects.filter(user=user)
    except :
        address = None
    
    context = {
        'user': user,
        'addrs': address
    }
    return render(request, 'userprofile.html', context)
    # if 'username' in request.session: 
    # user = User.objects.get(pk=id)
    # adrs={
    #         'addrs' : Address.objects.get(user=user)
    #      }
    # return render(request, 'userprofile.html', adrs)




def add_address(request,id):
    user = request.user
    uid = user.id
    state = ['Kerala', 'AndraPradesh', 'Karnataka', 'Tamilnadu']
    city = ['Kannur','Kozhikkode','Ernakulam', 'Kochi', 'Thiruvananthapuram','Banglore','Hubli','Hydrabad','Coimbator','Madurai']
    if request.method == 'POST':
        address = Address(
            user=request.user,
            firstname=request.POST['firstname'],
            lastname=request.POST['lastname'],
            phone=request.POST['phone'],
            email=request.POST['email'],
            address_line_1=request.POST['address_line_1'],
            address_line_2=request.POST.get('address_line_2', ''),
            # phone=request.POST['phone'],
            city=request.POST['city'],
            state=request.POST['state'],
            pincode=request.POST['pincode']
        )
        address.save()
        messages.success(request, 'Address Added successfully.')
        return redirect('userprofile', uid)
    
        # else :
        #     return redirect('checkout')
    else:
        context = {
            'state': state,
            'city': city,
        }
    return render(request, 'addaddress.html',context)

@login_required
def addreview(request):
    rating = [ 'Poor', 'Fair', 'Average', 'Good', 'Excellent']
    if request.method == 'POST':
        user = request.user.username
        product_id = request.POST['id']
        product = Variant.objects.get(pk=product_id)
        rating = request.POST['rating']
        comment = request.POST['comment']
        if rating == "":
            messages.warning(request, 'Please Select Your Rating.')
            return redirect('singleproduct',product_id)
        if comment == "":
            messages.warningq   (request, 'Please Add Some Comment.')
            return redirect('singleproduct',product_id)
        review = ProductReview.objects.create(user=user, product=product, rating=rating, comment=comment)
        messages.success(request, 'Review Added successfully.')
        return redirect('singleproduct',product_id)

def deladdress(request, id):
    address=Address.objects.get(pk=id)
    address.delete()
    uid = address.user.id
    messages.warning(request, 'Address Deleted.')
    return redirect('userprofile', uid)


def editprofile(request, id):
    state = ['Kerala', 'AndraPradesh', 'Karnataka', 'Tamilnadu']
    city = ['Kannur','Kozhikkode','Ernakulam','Thiruvananthapuram', 'Kochi', 'Banglore','Hubli','Hydrabad','Coimbator','Madurai']
    newaddress = Address.objects.get(pk= id)
    user = User.objects.get(email=newaddress.user.email)
    if request.method == 'POST':
        newaddress.firstname=request.POST['firstname']
        newaddress.lastname=request.POST['lastname']
        newaddress.email=request.POST['email']
        newaddress.address_line_1=request.POST['address_line_1']
        newaddress.address_line_2=request.POST.get('address_line_2', '')
        newaddress.phone=request.POST['phone']
        newaddress.city=request.POST['city']
        newaddress.state=request.POST['state']
        newaddress.pincode=request.POST['pincode']
        newaddress.save()
        return redirect('userprofile', user.id)
    
    context = {
        'state': state,
        'city' : city,
        'newaddress' : newaddress
    }

    return render(request, 'editprofile.html',context)

def changepassword(request):
     if request.method == 'POST':
        oldpass = request.POST['oldpassword']
        newpass = request.POST['password']
        confirm_newpass = request.POST['confirm_password']
        if len(newpass) < 6:
            messages.info(request,'Password should be at least 6 characters long')
            return redirect(changepassword)
        else:
            user = auth.authenticate(username=request.user.username, password=oldpass)
            if user:
                if newpass == confirm_newpass:
                    user.set_password(newpass)
                    user.save()
                    messages.success(request, "Password Changed")
                    return redirect(login_user)
                else:
                    messages.success(request, "Password not matching")
                    return redirect(changepassword)
            else:
                messages.success(request, "Invalid Password")
                return redirect(changepassword)
        
     return render(request, 'changepassword.html')

def index(request): 
    products = Product.objects.all()
    variant = Variant.objects.all()
    paginator = Paginator(variant, 8)
    page_numebr = request.GET.get('page')
    page_obj = paginator.get_page(page_numebr)
    dict_product={
            'var': variant,
            'page_obj':page_obj
            }
    return render(request, 'index.html', dict_product)

def logout(request): 
    request.session.flush()
    return redirect(login_user)

def category(request, cid):
    if cid == 0:
        products = Product.objects.all()
        variant = Variant.objects.all()
    else:
        category = get_object_or_404(Category, id=cid)
        variant = Variant.objects.filter(category=category)

    categories = Category.objects.all()
    paginator = Paginator(variant, 6)
    page_numebr = request.GET.get('page')
    page_obj = paginator.get_page(page_numebr)
    dict_product={
            'categories': categories,
            'var': variant,
            'page_obj':page_obj
            }
    return render(request, 'category.html', dict_product)

def singleproduct(request, id): 
    rating = [ 'Poor', 'Fair', 'Average', 'Good', 'Excellent']
    variant = Variant.objects.get(pk=id)
    review=ProductReview.objects.filter(product=variant)
    product = get_object_or_404(Product, name=variant.product)
    img = Variant.objects.filter(product=product)
    
    size = Size.objects.filter(variant=variant)
    if not size:
        size = None
        
    dict_product={
        'review':review,
        'rating': rating,
        'var':Variant.objects.get(pk=id),
        'img':img,  
        'size':size,         
    }
        
    # variant = Variant.objects.get(pk=id)
    # product = get_object_or_404(Product, name=variant.product)
    # img = Variant.objects.filter(product=product)
    # print(img,'--------------------------------------------------')
    
    # size = Size.objects.filter(variant=variant)
    # dict_product={
    #     'var':Variant.objects.get(pk=id),
    #     'img':img,  
    #     'size':size,         
    #               }
    return render(request, 'singleproduct.html', dict_product)

def search(request):
    keyword = request.GET.get('name')
    print(keyword)
    products = Variant.objects.filter(Q(product__name__icontains=keyword) | Q(color__icontains=keyword)).order_by('created')
    categories = Category.objects.all()
    paginator = Paginator(products, 6)
    page_numebr = request.GET.get('page')
    page_obj = paginator.get_page(page_numebr) 
    dict_product = {
        'categories': categories,
            'var': products,
            'page_obj':page_obj
        
    }
    return render(request, 'category.html', dict_product)

def userwishlist(request):
    user = request.user
    witems=wishlist.objects.filter(user_id=user.id)
    context={
        'witems':witems,
    }
    return render(request,'wishlist.html',context)

def add_to_wishlist(request,product_id):
    if request.user.is_authenticated:
        product = Variant.objects.get(id=product_id)
        user = request.user
        if wishlist.objects.filter(product=product,user_id=user.id).exists():
            messages.warning(request, "Product already exist in wishlist")
            return redirect(userwishlist)
            
        else:
            wishlist.objects.create(product=product,user_id=user.id)
            messages.success(request,"Product added to wishlist")
            return redirect(userwishlist)
            
    else:
        messages.warning(request, "Please log in to add items to wishlist.")
        return redirect(login_user)
    
def remove_from_wishlist(request,product_id):
    user = request.user
    wishItem=wishlist.objects.get(product_id=product_id,user_id=user.id)
    wishItem.delete()
    return redirect(userwishlist)


def viewcart(request):
    if request.user.is_authenticated:
        current_user = request.user

        items = CartItem.objects.filter(user_id=current_user.id).order_by('id')
        cart_items = []
        total = 0
        for cart_item in items:
            s = cart_item.size
            product = get_object_or_404(Variant, id=cart_item.product.id)
            size = Size.objects.filter(variant=product, size=s).first()
            quantity = cart_item.quantity
            price = product.price*quantity
            cart_items.append({'product':product,'quantity':quantity,'price':price}) 
            if size.stock == 0:
                pass
            else:
                total += price   
        context = { 'cart_items': cart_items, 'total': total }

    else:
        messages.warning(request, "Please log in to add items to cart.")
        return redirect(login_user)
    return render(request, 'viewcart.html',context)


def addtocart(request, variant_id):
        if request.user.is_authenticated:
            if request.method == 'POST':
            # Get the current user
                current_user = request.user
                
                # Get the selected quantity of the product
                try :
                    s = request.POST['size']
                except :
                    messages.error(request, "Please select the size and try again.")
                    return redirect(singleproduct,variant_id)
                variant = get_object_or_404(Variant, id=variant_id)
                size = Size.objects.filter(variant=variant, size=s).first()
                quantity = request.GET.get('quantity')
                if quantity is None:
                    product_quantity = 1
                else:
                    product_quantity = int(quantity)

                # Get the selected variant and size

                # Check if the item already exists in the cart
                item_exists = CartItem.objects.filter(user=current_user, product=variant, size=size).exists()
                if item_exists:
                    item = CartItem.objects.get(user=current_user, product=variant, size=size)
                    quantity_expected = item.quantity + product_quantity
                    
                    if size.stock >= quantity_expected:
                            item.quantity = item.quantity + product_quantity
                            item.save()
                            messages.success(request, f"{variant.product} ({size.size}) are added to the cart.")     
                    else:
                        item.quantity = size.stock
                        item.save()
                        messages.info(request, f"{size.stock} items left. All of them are added to the cart.")
                else:
                    if size.stock >= product_quantity:
                        CartItem.objects.create(user=current_user, product=variant, size=size, quantity=product_quantity)
                        messages.success(request, f"{variant.product} ({size.size}) added to cart!")
                    else:
                        product_quantity = size.stock
                        CartItem.objects.create(user=current_user, product=variant, size=size, quantity=product_quantity)
                        messages.info(request, f"{size.stock} items left. All of them are added to the cart.")

                return redirect('viewcart')    
        else:
            messages.warning(request, "Please log in to add items to cart.")
            return redirect(login_user)
    


def removecartproduct(request,product_id):
    current_user = request.user
    product=get_object_or_404(Variant,id=product_id)
    cart_item=CartItem.objects.get(user_id=current_user.id,product_id=product.id)
    cart_item.delete()
    return redirect(viewcart)

def addcartitem(request,product_id):
    if request.user.is_authenticated :
        current_user=request.user
        product = get_object_or_404(Variant, id=product_id)
        item = CartItem.objects.get(user_id=current_user.id, product=product)
        s = item.size
        size = Size.objects.filter(variant=product, size=s).first()

        
        item.quantity = item.quantity + 1
        if (size.stock>=item.quantity):
            item.save()
            return redirect(viewcart)
        else:
            messages.warning(request,"Product Out Of Stock...! Can't be added to cart")
            return redirect(viewcart)

    else:
        messages.warning(request, "Please log in to add items to cart.")
        return redirect(login_user)
    
def removecartitem(request,product_id):
    current_user = request.user
    product = get_object_or_404(Variant, id=product_id)

    cart_items = CartItem.objects.filter(user_id=current_user.id, product=product)
    print(cart_items)
    for cart_item in cart_items:
        if cart_item.quantity == 1:
            cart_item.delete()  # remove the item from the cart if the quantity is 1
        else:
            cart_item.quantity -= 1
            cart_item.save()  # decrement the quantity by 1
    return redirect(viewcart)

def checkout(request):
        if request.user.is_authenticated:
            current_user = request.user
            user = User.objects.get(pk=current_user.id)
            try:
                address = Address.objects.filter(user=user)
            except :
                address = None
            
            items = CartItem.objects.filter(user_id=current_user.id).order_by('id')
            cart_items = []
            total = 0
            for cart_item in items:
                s = cart_item.size
                print(s,"size of s in viewcart............................................")
                product = get_object_or_404(Variant, id=cart_item.product.id)
                size = Size.objects.filter(variant=product, size=s).first()
                quantity = cart_item.quantity
                price = product.price*quantity
                cart_items.append({'product':product,'quantity':quantity,'price':price}) 
                if size.stock == 0:
                    pass
                else:
                    shipping = 50
                    total += price   
                    tws =total+shipping

            context = { 
                'cart_items': cart_items, 
                'st': total, 
                'shp' : shipping, 
                'tws': tws, 
                'price':price, 
                'user': user,
                'addrs': address,
                }
        return render(request, 'checkout.html',context)


def contact(request):
        return render(request, 'contact.html')

# def confirmation(request):
#     return render(request, 'confirmation.html')

def confirmation(request, id):
    # try:
        cart_items=CartItem.objects.filter(user=request.user)
        # newAddress_id = request.POST.get('selected_addresses')
        addressid = request.POST.get('address')
        if addressid == None:
            messages.warning(request, "Please Select Your Address,  Or Add A New Address.")
            return redirect(checkout)
        address = Address.objects.get(pk=addressid)
        total=request.POST.get('total')
        Shipping=request.POST.get('shipping')
        amountToBePaid=request.POST.get('amountToBePaid')
        user = User.objects.get(pk=id)
        
        
        # if not newAddress_id:
        #     messages.error(request,'Select An Address to Proceed to Checkout.')
        #     return redirect(checkout)
        # else:
        #     address  = Address.objects.get(id = newAddress_id)

    # except ObjectDoesNotExist:
        # pass
        context={
            'cart_items':cart_items,
            'addressSelected':address,
            'shippingcharge':Shipping,
            'amountToBePaid':amountToBePaid,
            'total':total,
            'razor_key': trendshoes.settings.API_KEY
                }
        return render(request, 'confirmation.html', context)

def calculateCartTotal(request):
   cart_items   = CartItem.objects.filter(user=request.user)
   if not cart_items:
       pass
    #   return redirect('product_management:productlist',0)
   else:
      total = 0
      tax=0
      grand_total=0
      for cart_item in cart_items:
         total  += (cart_item.product.price * cart_item.quantity)
         tax = (5 * total) / 100
         grand_total = tax + total
   return total, tax, grand_total


# @login_required(login_url='login')
# @csrf_protect

def placeOrder(request):
   if request.method =='POST':
         
         newAddress_id = request.POST.get('addressSelected')
         address = Address.objects.get(id = newAddress_id)
         newOrder =Order()
         newOrder.user=request.user
         newOrder.address = address
         yr = int(datetime.date.today().strftime('%Y'))
         dt = int(datetime.date.today().strftime('%d'))
         mt = int(datetime.date.today().strftime('%m'))
         d = datetime.date(yr,mt,dt)
         current_date = d.strftime("%Y%m%d")
         rand = str(random.randint(1111111,9999999))
         order_number = current_date + rand
         newPayment = Payment()
         if('payment_id' in request.POST ):
            newPayment.payment_id = request.POST.get('payment_id')
            newPayment.paid = True
         else:
            newPayment.payment_id = order_number
            payment_id  =order_number
         newPayment.payment_method = request.POST.get('payment_method')
         newPayment.customer = request.user
         newPayment.save()
         newOrder.payment = newPayment
         try :
            total, tax, grand_total = calculateCartTotal(request)
         except:
             messages.success(request,  "Your Order Is Already Placed.")
             return redirect('viewcart')
         newOrder.order_total = grand_total
        
         newOrder.paid_amount = grand_total
         newPayment.amount_paid = grand_total
         newPayment.save()
         newOrder.payment = newPayment
         order_number = 'Trends'+ order_number
         newOrder.order_number =order_number
        #  #to making order number unique
         while Order.objects.filter(order_number=order_number) is None:
            order_number = 'Trends'+order_number
         newOrder.tax=tax
         newOrder.save()
         newPayment.order_id = newOrder.id
         newPayment.save()
         newOrderItems = CartItem.objects.filter(user=request.user)
         for item in newOrderItems:
            OrderProduct.objects.create(
                order = newOrder,
                customer=request.user,
                product=item.product,
                product_price=item.product.price,
                quantity=item.quantity
            )
            #TO DECRESE THE QUANTITY OF PRODUCT FROM CART
            variant = Variant.objects.filter(id=item.product_id).first()
            s= item.size
            orderproduct = Size.objects.filter(variant=variant, size=s).first()
            if(orderproduct.stock<=0):
               messages.warning(request,'Sorry, Product out of stock!')
               orderproduct.is_available = False
               orderproduct.save()
               item.delete()
               return redirect('viewcart')
            elif(orderproduct.stock < item.quantity):
               messages.success(request,  f"{orderproduct.stock} only left in cart.")
               return redirect('viewcart')
            else:
               orderproduct.stock -=  item.quantity
            orderproduct.save()
        #  if(instance):
        #     instance.order = newOrder
        #     instance.save()
        # TO CLEAR THE USER'S CART
         cart_item=CartItem.objects.filter(user=request.user)
         cart_item.delete()
         messages.success(request,'Order Placed Successfully')
         payMode =  request.POST.get('payment_method')
         if (payMode == "Paid by Razorpay" ):
            return JsonResponse ({'order_number':order_number,'status':"Your order has been placed successfully"})
         elif (payMode == "COD" ):
            request.session['my_context'] = {'payment_id':payment_id}
            return redirect('order_complete', newOrder.order_number )
   return redirect('checkout')

@login_required(login_url='login')
@csrf_protect
def orderComplete(request,ordernumber):
    order = Order.objects.get(order_number=ordernumber)
    orderitems = OrderProduct.objects.filter(order=order)
    context={
        'total':order.order_total,
        'order': order,
        'orderitems':orderitems,    
        # 'product_items': product_items,
    }

    return render(request, 'ordercomplete.html',context)

def razorPayCheck(request):
   total=0
#    coupon_discount =0
   amountToBePaid = 0
   current_user=request.user
   cart_items=CartItem.objects.filter(user_id=current_user.id)
   if cart_items:
      for cart_item in cart_items:
         total+=(cart_item.product.price*cart_item.quantity)
      tax=(5 * total)/100
      grand_total=total+tax
      grand_total = round(grand_total,2)
      amountToBePaid = grand_total
      return JsonResponse({
         'grand_total' : grand_total,
        #  'coupon': coupon,
        #  'coupon_discount':coupon_discount,
         'amountToBePaid':amountToBePaid
      })
   else:
      return redirect('categary',0)
   
def myorders(request):
    orders = Order.objects.filter(user=request.user).order_by('id').reverse()
    return render(request, 'myorders.html', {'orders': orders})


@login_required(login_url='login')
def cancelOrder(request):
    if request.method == 'POST':
            id = request.POST.get('id')

    client = razorpay.Client(auth=(trendshoes.settings.API_KEY, trendshoes.settings.RAZORPAY_SECRET_KEY))
    try:
        order = Order.objects.get(id=id,user=request.user)
    except Order.DoesNotExist:
        # Handle the case where the order does not exist
        order = None
    
    if order is None:
        # Render an error message if the order does not exist
        messages.warning(request,'The order you are trying to cancel does not exist.')
        return redirect(myorders)
    
    payment=order.payment
    msg=''
    
    if (payment.payment_method == 'Paid by Razorpay'):
        payment_id = payment.payment_id
        amount = payment.amount_paid
        amount= amount*100
        try :
            captured_amount = client.payment.capture(payment_id,amount)
        except BadRequestError as e:
            # Handle a BadRequestError from Razorpay
            captured_amount = None
            messages.warning(request,'The payment has not been captured.Please try again later. If the issue continues, CONTACT THE SUPPORT TEAM!')
            return redirect(myorders)
        #   except ServerError as e:
              # Handle a ServerError from Razorpay
        #   captured_amount = None
            # msg = "Server error occurred while capturing the payment."

        if captured_amount is not None and captured_amount['status'] == 'captured' :
            refund_data = {
                "payment_id": payment_id,
                "amount": amount,  # amount to be refunded in paise
                "currency": "INR",
            }
            
            refund = client.payment.refund(payment_id, refund_data)
            #  except BadRequestError as e:
            #      # Handle a BadRequestError from Razorpay
            #      refund = None
            #      msg = "Bad request error occurred while processing the refund."
            #  except ServerError as e:
            #      # Handle a ServerError from Razorpay
            #      refund = None
            #      msg = "Server error occurred while processing the refund."
            print(refund)
            
            if refund is not None:
                current_user=request.user
                order.refund_completed = True
                order.status = 'Cancelled'
                payment = order.payment
                payment.refund_id = refund['id']
                payment.save()
                order.save()
                messages.success(request,'Your order has been successfully cancelled and amount has been refunded!')
                mess=f'Hai\t{current_user.username},\nYour order has been cancelled, Money will be refunded with in 1 hour\nThanks!'
                try:
                    send_mail(
                            "Order Cancelled",
                            mess,
                            settings.EMAIL_HOST_USER,
                            [current_user.email],
                            fail_silently = False
                        )
                except Exception as e:
                    # Handle an exception while sending email
                    msg += "\nError occurred while sending an email notification."
            else :
                messages.warning(request,'Your order is not cancelled because the refund could not be completed now. Please try again later. If the issue continues, CONTACT THE SUPPORT TEAM!')
                pass
        else :
            if(payment.paid):
                order.refund_completed = True
                order.status = 'Cancelled'
                messages.success(request,'YOUR ORDER HAS BEEN SUCCESSFULLY CANCELLED!')
                order.save()
            else:
                order.status = 'Cancelled'
                order.save()
                messages.success(request,'Your payment has not been recieved yet. But the order has been cancelled.!')
    else :
        order.status = 'Cancelled'
        messages.success(request,'YOUR ORDER HAS BEEN SUCCESSFULLY CANCELLED!')
        order.save()
    return redirect(myorders)

def viewOrder(request, id):
    order =Order.objects.filter(id=id,user=request.user).first()
    orderitems = OrderProduct.objects.filter(order=order)

    context={
        'order': order,
        'orderitems':orderitems,
    }
    return render(request,'vieworder.html',context)




