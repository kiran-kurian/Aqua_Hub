from urllib import request
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from aquaapp.models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password
from django.shortcuts import render, get_object_or_404
from .models import Seller
import re 
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.views.decorators.cache import never_cache   
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.conf import settings
import razorpay
from django.views.decorators.csrf import csrf_exempt





# Create your views here.
def index_view(request):
    return render(request, 'index.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                request.session['master']=username
                return redirect('approve')
            else:
                request.session['user']=username
                return redirect('product_list')
        else:
            
            return render(request,'userlogin.html',{
                'message':"Invalid Username Or Password"
            })
            
    return render(request, 'userlogin.html')

def seller_view(request):
    return render(request, 'sellerlogin.html')

def user_reg(request):
       if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        email = request.POST.get('email')
        number = request.POST.get('contact_number')
        address = request.POST.get('address')

        # Check if any required field is empty
        if not username or not password or not confirm_password or not email or not number or not address:
            return render(request, 'usereg.html', {
                "messages": "All fields are required."
            })

        # Password validation: check if passwords match
        if password != confirm_password:
            return render(request, 'usereg.html', {
                "messages": "Passwords do not match."
            })

        # Password strength validation: Minimum 8 characters, at least one uppercase letter, one lowercase letter, and one digit
        if len(password) < 8 or not re.search(r'[A-Z]', password) or not re.search(r'[a-z]', password) or not re.search(r'\d', password):
            return render(request, 'usereg.html', {
                "messages": "Password must be at least 8 characters long, contain one uppercase letter, one lowercase letter, and one digit."
            })

        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            return render(request, 'usereg.html', {
                "messages": "Enter a valid email address."
            })

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return render(request, 'usereg.html', {
                "messages": "Username already exists."
            })

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return render(request, 'usereg.html', {
                "messages": "Email already exists."
            })

        # Validate phone number format: Ensure it contains only digits and is of valid length (e.g., 10 digits)
        if not re.match(r'^\d{10}$', number):
            return render(request, 'usereg.html', {
                "messages": "Enter a valid 10-digit phone number."
            })

        # Create user
        try:
            user = userreg.objects.create_user(
                username=username,
                email=email,
                password=password,
                phone_number=number,
                address=address
            )
            # user.profile.phone_number = number
            # user.profile.address = address
            user.save()

            messages.success(request, "Registration successful. You can now log in.")
            return redirect('login')
        except Exception as e:
            # Handle exceptions (e.g., database errors)
            return render(request, 'usereg.html', {
                "messages": "An error occurred during registration. Please try again."
            })

       return render(request, 'usereg.html')

def admin_view(request):
    return render(request, 'admin.html')

# def seller_reg(request):
#  from django.shortcuts import render, redirect
# from django.contrib.auth.models import User
# from .models import Seller

from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from .models import Seller  # Import your Seller model
from django.core.files.storage import FileSystemStorage  # To handle file uploads

def seller_reg(request):
    if request.method == 'POST':
        shop_name = request.POST.get('shop_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        location = request.POST.get('location')
        contact_num = request.POST.get('contact_num')
        product_type = request.POST.get('product_type')

        # Handle file upload for the licensing document
        if request.FILES.get('licensing_document'):
            licensing_document = request.FILES['licensing_document']
            fs = FileSystemStorage()
            filename = fs.save(licensing_document.name, licensing_document)
            licensing_document_url = fs.url(filename)  # Get the file's URL (optional)

            # Create the Seller object with the uploaded file
            Seller.objects.create(
                username=username,
                shop_name=shop_name,
                email=email,
                password=make_password(password),
                location=location,
                contact_num=contact_num,
                product_type=product_type,
                licensing_document=filename  # Save the file name to the licensing_document field
            )
        
        return redirect('slogin')  # Replace with your success URL

    return render(request, 'sellereg.html')


 
 
def user_home(request):
    return render(request, 'products.html')


def about_view(request):
    return render(request, 'about.html')




from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.shortcuts import redirect, render
from .models import Seller

def seller_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        shop_name = request.POST['shop_name']
        password = request.POST['password']

        # Try to find the seller by both username and shop_name
        try:
            seller = Seller.objects.get(username=username, shop_name=shop_name)
        except Seller.DoesNotExist:
            messages.error(request, 'Invalid username, shop name, or password')
            return redirect('slogin')

        # Check if seller is approved
        if not seller.approved:
            messages.error(request, 'Your account is not approved yet. Please wait for admin approval.')
            return redirect('slogin')

        # Check the password
        if check_password(password, seller.password):  # Assuming password is hashed
            # Set the seller session if authenticated
            request.session['seller_id'] = seller.id
            request.session['seller_username'] = seller.username
            request.session['seller_shop_name'] = seller.shop_name

            return redirect('sellerproduct')
        else:
            messages.error(request, 'Invalid username, shop name, or password')
            return redirect('slogin')
    
    return render(request, 'sellerlogin.html')



def logout_view(request):
    request.session.flush()
    logout(request)
    return redirect('index')
    



def seller_dash(request):
    return render(request, 'sellerdash.html')


@never_cache
def admin_approv(request):
    if 'master' in request.session:
    # Fetch all sellers whose 'approved' field is False (i.e., pending approval)
        pending_sellers = Seller.objects.filter(approved=False)

        # Render the 'adminapprov.html' template with the pending sellers data
        return render(request, 'adminapprov.html', {'pending_sellers': pending_sellers})
    else:
        return redirect('login')

def approve_seller(request, id):
    
    seller = get_object_or_404(Seller,pk=id)
    seller.approved=True    
    seller.save()
    return redirect('approve')


@never_cache
def approved_seller(request):
    if 'master' in request.session:
        # Fetch all sellers who are approved
        approved_sellers = Seller.objects.filter(approved=True)
        
        return render(request, 'approvedsellers.html', {'approved_sellers': approved_sellers})
    else:
        return redirect('login')
    

from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Seller

@login_required
def approve_seller(request, seller_id):
    seller = get_object_or_404(Seller, id=seller_id)
    seller.approved = True  # Approve the seller
    seller.save()
    messages.success(request, 'Seller approved successfully!')
    return redirect('admin_approval_page')  # Redirect to approval page


@login_required
def reject_seller(request, seller_id):
    seller = get_object_or_404(Seller, id=seller_id)

    if request.method == 'POST':
        reason = request.POST.get('reason')
        
        # Send rejection email
        send_mail(
            'Aqua Hub - Seller Registration Rejected',
            f'Hello {seller.username},\n\nYour seller registration was rejected for the following reason:\n{reason}\n\nThank you for your interest in Aqua Hub.',
            'aquahub837@gmail.com',  # Replace with your email
            [seller.email],
            fail_silently=False,
        )

        # Delete the seller record after rejection
        seller.delete()

        messages.success(request, 'Seller rejected and email sent!')
        return redirect('approve')  # Redirect to the approval page



    
def remove_seller(request, seller_id):
    # Fetch the seller by id
    seller = get_object_or_404(Seller, id=seller_id)
    
    if request.method == 'POST':
        # Remove the seller or change the approved status to False
         # This will remove the seller completely
        # Alternatively, you can mark the seller as unapproved:
         seller.approved = False
         seller.save()

        # Redirect back to the list of approved sellers
    return redirect('sellerappr')

    return render(request, 'approvedsellers.html')






def add_product(request):
    seller_id = request.session.get('seller_id')
    sellers = get_object_or_404(Seller,pk=seller_id)
    print(sellers.product_type)
    if request.method == 'POST':
        # Fetch the currently logged-in seller by their username
        

        if not seller_id:
            messages.error(request, "No Seller matches the given query.")
            return redirect('sellerdash')  # or another appropriate page

        # Get product details from the form (example: name, price, stock, etc.)
        # seller = Seller.objects.get(id=seller_id)
        product_name = request.POST.get('product_name')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        description = request.POST.get('description')  # Get description from form
        image = request.FILES.get('image')
        water_quality = request.POST['water_quality']
        tank_size = request.POST['tank_size']
        feeding = request.POST['feeding']
        behavior = request.POST['behavior']
        health_issues = request.POST['health_issues']

        # Create a new product and associate it with the seller
        product = Product.objects.create(
            seller=sellers, 
            product_name=product_name, 
            price=price,
            stock=stock,
            description=description,
            image=image,
            water_quality=water_quality,
            tank_size=tank_size,
            feeding=feeding,
            behavior=behavior,
            health_issues=health_issues,
        )
        product.save()
        messages.success(request, "Product added successfully!")
        return redirect('sellerproduct')

    return render(request, 'add_product.html',{'sellers':sellers})





from django.db.models import Q  # For complex queries

@never_cache
def seller_product(request):
    if 'seller_id' in request.session:
        # Fetch the currently logged-in seller's ID from session
        seller_id = request.session.get('seller_id')

        if not seller_id:
            messages.error(request, "You must be logged in as a seller.")
            return redirect('sellerdash')  # Redirect to seller dashboard if not logged in

        # Get the seller's details
        seller = Seller.objects.get(id=seller_id)

        # Fetch all products added by the seller
        products = Product.objects.filter(seller=seller)

        # Check if there's a search query
        query = request.GET.get('q')
        if query:
            products = products.filter(
                Q(product_name__icontains=query) |
                Q(description__icontains=query)
            )

        return render(request, 'sellerproduct.html', {'products': products})
    else:
        return redirect('slogin')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            # Generate password reset token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            # Send the reset email
            reset_url = request.build_absolute_uri(f'/reset_password/{uid}/{token}/')
            subject = 'Reset Your Password'
            message = render_to_string('password_reset_email.html', {
                'user': user,
                'reset_url': reset_url,
            })
            send_mail(subject, message, 'aquahub837@gmail.com', [user.email], html_message=message)
            return render(request, 'userlogin.html', {"message": "Password reset link is sent"})
        except User.DoesNotExist:
            return render(request, 'forgotpassword.html', {'error': 'No user found with that email.'})
    return render(request, 'forgotpassword.html')


def reset_password(request, uidb64, token):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if password != confirm_password:
            return render(request, 'resetpassword.html', {'error': 'Passwords do not match'})
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            if default_token_generator.check_token(user, token):
                # Update the user's password
                user.set_password(password)
                user.save()
                logout(request)
                return render(request, 'userlogin.html', {"message": "Reset complete, Login now"})
        except User.DoesNotExist:
            return render(request, 'resetpassword.html', {'error': 'Invalid link'})
    return render(request, 'resetpassword.html')



def edit_view(request, product_id):
    # Get the product by ID or return a 404 if not found
    product = get_object_or_404(Product, id=product_id)
    
    # Check if the form is submitted via POST request
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        description = request.POST.get('description')
        water_quality = request.POST.get('water_quality')
        tank_size = request.POST.get('tank_size')
        feeding = request.POST.get('feeding')
        behavior = request.POST.get('behavior')
        health_issues = request.POST.get('health_issues')
        
        # Validate inputs
        if not product_name or not description:
            messages.error(request, 'Product name and description cannot be empty.')
        elif float(price) < 0:
            messages.error(request, 'Price should be a positive number.')
        elif not stock.isdigit() or int(stock) < 0:
            messages.error(request, 'Stock should be a non-negative integer.')
        else:
            # Update the product details
            product.product_name = product_name
            product.price = float(price)
            product.stock = int(stock)
            product.description = description
            product.water_quality = water_quality
            product.tank_size = tank_size
            product.feeding = feeding
            product.behavior = behavior
            product.health_issues = health_issues
            
            # Handle image upload
            if 'image' in request.FILES:
                product.image = request.FILES['image']
            
            product.save()  # Save the updated product details
            
            messages.success(request, 'Product updated successfully!')
            return redirect('sellerproduct')  # Redirect to seller dashboard or product listing
    
    context = {
        'product': product
    }
    
    return render(request, 'editproduct.html', context)


def disable_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if 'seller_id' in request.session:
        product.is_active = False
        product.save()
        messages.success(request, f"{product.product_name} has been disabled.")
    else:
        messages.error(request, "You are not authorized to disable this product.")
    
    return redirect('sellerproduct') 


def enable_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if 'seller_id' in request.session:
        product.is_active = True
        product.save()
        messages.success(request, f"{product.product_name} has been enabled.")
    else:
        messages.error(request, "You are not authorized to disable this product.")
    
    return redirect('sellerproduct') 



@never_cache
def product_list_view(request):
    # Get the search query, letter filter, and sort order if available
    query = request.GET.get('q')
    letter = request.GET.get('letter')
    sort = request.GET.get('sort')  # Sorting order (price-asc or price-desc)

    # Fetch all approved and active products
    products = Product.objects.filter(is_active=True)

    # Filter products by search query if provided
    if query:
        products = products.filter(product_name__icontains=query)

    # Filter products by the first letter if a letter is selected
    if letter:
        products = products.filter(product_name__istartswith=letter)  # Case-insensitive filtering by first letter

    # Sort products by price if sorting is selected
    if sort == 'price-asc':
        products = products.order_by('price')
    elif sort == 'price-desc':
        products = products.order_by('-price')

    # Set up pagination (e.g., 9 products per page)
    paginator = Paginator(products, 9)  # Show 9 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Pass paginated products, search query, letter, and sort option to the template
    context = {
        'products': page_obj,
        'query': query,  # Retain the search query in the search bar
        'letter': letter,  # Retain the selected letter for alphabetical filtering
        'sort': sort  # Retain the sort option in the sort dropdown
    }

    return render(request, 'products.html', context)



        

def product_detail(request, product_id):
    # Get the product by its ID, or return a 404 error if not found
    product = get_object_or_404(Product, id=product_id)
    
    # Render the product detail template with product data
    context = {
        'product': product,
    }
    return render(request, 'product_detail.html', context)


@never_cache
@login_required(login_url='login')
def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        messages.error(request, 'Please log in to add items to your cart.')
        return redirect('login')

    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity',1)) # Get quantity from the form

    # Check if the user already has a cart
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Check if the product is already in the cart
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, quantity=quantity)
    
    if not created:
        cart_item.quantity += quantity  # Update quantity if it already exists
    cart_item.save()

    messages.success(request, f'{product.product_name} has been added to your cart.')
    return redirect('view_cart')  # Redirect to view cart page


@login_required(login_url='login')
def view_cart(request):
    if 'user' in request.session:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all()
        total_price = sum(item.get_total_price() for item in cart_items)
        context = {
            'cart_items': cart_items,
            'total_price': total_price,
        }
        return render(request, 'cart.html', context)

    else:
        return redirect('login')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('view_cart')


@login_required(login_url='login')
def book_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if not request.user.is_authenticated:
        messages.error(request, 'Please login to book this product.')
        return redirect('login')
    

@never_cache
@login_required(login_url='login')
def profile_view(request):
    if 'user' in request.session:
        user = request.user.userreg
        # Fetch the related usereg record
        
        if request.method == 'POST':
            # Get user details from the form
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            phone_number = request.POST.get('phone_number')
            
            
            # Update user fields
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.phone_number =phone_number
            
            # Update the phone number in usereg table
            

            user.save()  # Save the updated user details
        
            messages.success(request, 'Profile updated successfully!')
            return redirect('product_list')  # Redirect to profile page after saving

        context = {
            'user': user,
            
        }

        return render(request, 'profile_edit.html', context)
    else:
        return redirect('login')





def edit_seller_profile(request):
    # Check if seller is logged in by checking session
    
    if 'seller_id' not in request.session:
        messages.error(request, 'You need to log in to access this page.')
        return redirect('slogin')  # Redirect to login page if not authenticated

    # Get the seller ID from session
    seller_id = request.session['seller_id']

    # Fetch the seller instance based on the seller ID stored in the session
    seller = Seller.objects.get(id=seller_id)

    if request.method == 'POST':
        # Update the seller's information
        seller.email = request.POST.get('email')
        seller.contact_num = request.POST.get('contact_num')
        seller.location = request.POST.get('location')

        # Validate the input data as needed
        if not seller.email or not seller.contact_num or not seller.location:
            messages.error(request, 'All fields are required.')
        else:
            # Save the updated seller information
            seller.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('sellerproduct')  # Redirect to the profile page after saving

    # Render the profile editing template with current seller data
    context = {
        'seller': seller
    }
    return render(request, 'seller_profile.html', context)



def create_virtual_tank(request):
    if 'height' in request.GET and 'width' in request.GET:
        height = int(request.GET.get('height'))
        width = int(request.GET.get('width'))
        depth = int(request.GET.get('depth'))

        # Create a new VirtualTank entry
        VirtualTank.objects.create(user=request.user, height=height, width=width, depth=depth)

        return redirect('virtual_tank_view')  # Redirect to the tank view or another page

    return render(request, 'vtank.html')

def view_virtual_tank(request):
    # Get the latest virtual tank created by the user
    virtual_tank = VirtualTank.objects.filter(user=request.user).order_by('-created_at').first()

    context = {
        'virtual_tank': virtual_tank
    }
    return render(request, 'view_virtual_tank.html', context)


def blog_list(request):
    query = request.GET.get('q')  # Get the search query from the URL parameters
    if query:
        # Filter blogs based on the search query in the title
        blogs = BlogPost.objects.filter(Q(title__icontains=query)).order_by('-created_at')
    else:
        # If no search query, display all blogs
        blogs = BlogPost.objects.all().order_by('-created_at')

    return render(request, 'blog_list.html', {'blogs': blogs, 'query': query})

# Detail view for a single blog post
def blog_detail(request, pk):
    blog = get_object_or_404(BlogPost, pk=pk)
    return render(request, 'blog_detail.html', {'blog': blog})

# View for creating a new blog post (no forms used)

@login_required
def create_blog(request):
    if request.method == 'POST':
        print("dd")
        title = request.POST.get('title')
        print(title)
        content=request.POST.get('content')
        
        allow_comments = request.POST.get('allow_comments') == 'on'  # Checkbox
        image = request.FILES.get('image')

        if title and content :
            print("gg")
            blog_post = BlogPost.objects.create(
                title=title,
                content=content,
                author=request.user,
                allow_comments=allow_comments,
                image=image
            )
            blog_post.save()
            return redirect('blog_list')  # Redirect to the list of blogs

    return render(request, 'create_blog.html')

@login_required
def add_comment(request, blog_id):
    if request.method == 'POST':
        blog = get_object_or_404(BlogPost, id=blog_id)
        content = request.POST.get('content')
        if content:
            comment = Comment(blog=blog, user=request.user, content=content)
            comment.save()
        return redirect('blog_detail', pk=blog_id)


@login_required
def my_blogs(request):
    user_blogs = BlogPost.objects.filter(author=request.user)
    return render(request, 'my_blogs.html', {'blogs': user_blogs})


from django.shortcuts import redirect

@login_required
def edit_blog(request, blog_id):
    blog = get_object_or_404(BlogPost, id=blog_id)

    # Ensure that the logged-in user is the author of the blog post
    if blog.author != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        blog.title = request.POST.get('title')
        blog.content = request.POST.get('content')

        if 'image' in request.FILES:
            blog.image = request.FILES['image']

        blog.save()
        return redirect('my_blogs')  # Redirect to 'myblogs' after editing

    return render(request, 'edit_blog.html', {'blog': blog})

@login_required
def manage_users(request):
    users = User.objects.all()  # Fetch all users

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        action = request.POST.get("action")
        user = get_object_or_404(User, id=user_id)

        if action == "block":
            user.is_active = False
            user.save()
            # Send email to notify user
            send_mail(
                'Account Blocked',
                'Your account has been blocked. Please contact support for further details.',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            messages.success(request, f"{user.username} has been blocked.")
        elif action == "unblock":
            user.is_active = True
            user.save()
            # Send email to notify user
            send_mail(
                'Account Unblocked',
                'Your account has been unblocked. You can now log in again.',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            messages.success(request, f"{user.username} has been unblocked.")
        
        return redirect('manage_users')

    return render(request, 'admin_users.html', {'users': users})



@login_required
def register_complaint(request):
    if request.method == "POST":
        seller_id = request.POST.get('seller_id')
        payment_id = request.POST.get('payment_id')  # Get the order ID from the form
        subject = request.POST.get('subject')
        description = request.POST.get('description')

        try:
            # Get the seller based on the selected seller ID
            seller = Seller.objects.get(id=seller_id, approved=True)
        except Seller.DoesNotExist:
            messages.error(request, "Selected seller is not valid.")
            return redirect('register_complaint')

        # Ensure that the order ID is not empty
        if not payment_id:
            messages.error(request, "Order ID cannot be empty.")
            return redirect('register_complaint')

        # Create and save the complaint
        complaint = Complaint.objects.create(
            user=request.user,
            seller=seller,
            subject=subject,
            description=description,
            payment_id=payment_id  # Save the order ID in the complaint
        )
        messages.success(request, "Your complaint has been registered.")
        return redirect('register_complaint')

    # Fetch all approved sellers
    approved_sellers = Seller.objects.filter(approved=True)
    return render(request, 'register_complaint.html', {'approved_sellers': approved_sellers})



# @login_required(login_url='slogin')
def view_complaints(request):
    # Ensure the seller is logged in
    if 'seller_id' in request.session:
        seller_id = request.session.get('seller_id')

        # Fetch complaints related to the logged-in seller
        complaints = Complaint.objects.filter(seller__id=seller_id).order_by('-created_at')

        return render(request, 'seller_complaints.html', {'complaints': complaints})
    else:
        return redirect('slogin') 
    

    

@login_required
def add_new_address(request, product_id):
    product = Product.objects.get(id=product_id)
    quantity = request.POST.get('quantity', 1)
    print(quantity)
    if request.method == 'POST':
        # Collect form data
        full_name = request.POST.get('full_name')
        contact1 = request.POST.get('contact1')
        contact2 = request.POST.get('contact2')
        locality = request.POST.get('locality')
        address = request.POST.get('address')
        landmark = request.POST.get('landmark')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')
        save_address = request.POST.get('save_address')  # Check if the user wants to save the address

        # Validate and save the address
        if full_name and contact1 and address and city and state and pincode:
            
            # Check if the "Save this address" checkbox was checked
            if save_address:
                
                # Save the address to the UserAddress model
                address1=UserAddress.objects.create(
                    user=request.user,
                    full_name=full_name,
                    contact1=contact1,
                    contact2=contact2,
                    locality=locality,
                    address=address,
                    landmark=landmark,
                    city=city,
                    state=state,
                    pincode=pincode,
                    saved=True  # Mark the address as saved
                )
                address1.save()
                messages.success(request, "Address saved successfully!")
                print("jj")

            # After address submission, redirect to the order confirmation page (or the next step)
            return redirect('book_now', product_id=product.id, quantity=quantity)

        else:
            messages.error(request, "Please fill in all the required fields.")

    # Render the address form
    return render(request, 'addresss.html', {'product': product, 'quantity': quantity})


@login_required
def select_address(request, product_id):
    # Get quantity from POST or set a default value of 1 if it doesn't exist
    quantity = request.POST.get('quantity', 1)
    product = Product.objects.get(id=product_id)

    # Fetch saved addresses for the logged-in user
    user_addresses = UserAddress.objects.filter(user=request.user)

    context = {
        'user_addresses': user_addresses,
        'product_id': product_id,
        'quantity': quantity,
        'product': product,
    }

    return render(request, 'address.html', context)




def book_now(request, product_id,quantity):
    product = get_object_or_404(Product, id=product_id)
    # quantity = int(request.POST.get('quantity', 1))  # Get the selected quantity from POST data
    address_id=request.POST.get('selected_address')
    print(address_id)
     # Calculate total price
    total_price = product.price * quantity

    # Apply delivery charge if total_price is greater than 499
    delivery_charge = 40 if total_price < 499 else 0
    final_price = total_price + delivery_charge

    return render(request, 'book_now.html', {
        'product': product,
        'quantity': quantity,
        'total_price': total_price,
        'delivery_charge': delivery_charge,
        'final_price': final_price,
        'address': address_id    })


@login_required
def create_order(request, product_id):
    product = Product.objects.get(id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    address_id = request.POST.get('address')
    # Check if sufficient stock is available
    if product.stock < quantity:
        messages.error(request, "Insufficient stock available!")
        return redirect('product_detail', product_id=product_id)

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    # Fetch user's saved address (you can customize this to allow address selection)
    user_address = UserAddress.objects.get(id=address_id)

    total_price = product.price * quantity

    # Apply delivery charge if total_price is greater than 499
    delivery_charge = 40 if total_price < 499 else 0
    final_price = total_price + delivery_charge

    # Create the order in the database
    order = Order.objects.create(
        user=request.user,
        product=product,
        quantity=quantity,
        total_price=final_price,
        address=user_address
    )

    # Create a Razorpay order
    razorpay_order = client.order.create({
        'amount': int(final_price * 100),  # Amount in paisa (INR)
        'currency': 'INR',
        'payment_capture': '1'
    })

    # Store the Razorpay order ID
    order.payment_id = razorpay_order['id']
    order.save()

    context = {
        'order': order,
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'final_price': final_price,
    }

    return render(request, 'order_summary.html', context)




@csrf_exempt 
def payment_handler(request):
    if request.method == 'POST':
        # Extract the payment information from Razorpay's response
        payment_id = request.POST.get('razorpay_payment_id')
        order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')

        # Initialize the Razorpay client for payment verification
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        try:
            # Verify the payment signature to ensure the request is valid
            client.utility.verify_payment_signature({
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            })

            # Fetch the order using the payment ID
            order = Order.objects.get(payment_id=order_id)

            # Update the order payment status to 'Completed'
            order.payment_status = 'Completed'
            order.save()

            # Reduce stock for the ordered product
            product = order.product
            if product.stock >= order.quantity:  # Check if stock is available
                product.stock -= order.quantity
                product.save()
            else:
                # If stock is insufficient, you may want to handle this scenario
                order.payment_status = 'Failed'
                order.save()
                return render(request, 'payment_failed.html', {'order': order, 'error': 'Insufficient stock to fulfill the order'})

            # Payment success, return success response
            return render(request, 'payment_success.html', {'order': order})

        except razorpay.errors.SignatureVerificationError as e:
            # Handle payment verification failure
            order = Order.objects.get(payment_id=order_id)
            order.payment_status = 'Failed'
            order.save()

            # Log the error and show a failure page to the user
            return render(request, 'payment_failed.html', {'order': order, 'error': 'Payment verification failed. Please try again.'})
    
    return HttpResponseBadRequest("Invalid request method")

        

@login_required
def completed_orders(request):
    # Filter only orders that have been delivered
    completed_orders = Order.objects.filter(user=request.user, payment_status='Completed').order_by('-created_at')
    return render(request, 'completed_orders.html', {'completed_orders': completed_orders})




def seller_orders(request):
    # Assuming the seller's ID is stored in the session upon login
    seller_id = request.session.get('seller_id')

    # Fetch the seller's details using the seller ID
    seller = Seller.objects.get(id=seller_id)

    # Get all products added by this seller
    products = Product.objects.filter(seller=seller)

    # Fetch orders related to these products
    orders = Order.objects.filter(product__in=products).order_by('-created_at')

    return render(request, 'seller_orders.html', {'orders': orders})


@login_required # This decorator ensures that only admin users can access the page
def admin_all_orders(request):
    # Fetch all orders
    orders = Order.objects.all().order_by('-created_at')  # Assuming 'created_at' is a field in Order model

    return render(request, 'admin_orders.html', {'orders': orders})


# Make sure your Complaint model is imported


def reply_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    user_email = complaint.user.email  # Fetch user's email from the Complaint model's user relationship

    if request.method == 'POST':
        # Compose the response email (this could be a predefined message or dynamically composed)
        response = request.POST.get('response')
        subject = f"Response to your complaint: {complaint.subject}"
        message = f"""Dear {complaint.user.username},

Thank you for bringing your concern to our attention. We value your feedback and are committed to ensuring you have a positive experience with us.

Response to your complaint:
{response}

If you have further questions or require additional assistance, please feel free to reach out. We appreciate your patience and understanding as we work to address this matter.

Warm regards,  
[Seller's Name or Team]
Aqua Hub Support Team
"""

        try:
            send_mail(
                subject,
                message,
                'aquahub837@gmail.com',  # Replace with the seller's or platform's email
                [user_email],
            )
            messages.success(request, f"Reply email successfully sent to {complaint.user.username}.")
        except Exception as e:
            messages.error(request, f"Failed to send reply. Error: {e}")

    return redirect('view_complaints')  # Redirect back to the complaints list
