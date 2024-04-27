from decimal import Decimal
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import Category,BannerAdvertisement, PaymentMethod,SubCategory,Cart,OrderItem,Order,Product,ProductPhoto,ProductReview
from django.http import HttpResponse, JsonResponse
import json
from django.db.models import Count,Q,Max,Min
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_POST

def error_404(request, exception):
    return render(request, '404.html', status=404)

def error_500(request):
    return render(request, '500.html', status=500)

def offline_view(request):
    return render(request, 'offline.html')

def signup(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validate form data
        if not (full_name and email and username and password and confirm_password):
            messages.error(request, 'All fields are required.')
            return redirect('signup')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('signup')

        # Check if username or email already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken.')
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered.')
            return redirect('signup')

        # Create the user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = full_name
        user.save()

        messages.success(request, 'You have successfully signed up. Please log in.')
        return redirect('login') 

    return render(request, 'signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        reset_password = 'reset_password' in request.POST

        if reset_password:
            if username:
                user = User.objects.filter(username=username).first()
                if user:
                    return redirect('password_reset_done')
                else:
                    messages.warning(request, 'Username does not exist.')
                    return redirect('password_reset')
            else:
                messages.warning(request, 'Please enter your username before resetting the password.')
                return redirect('password_reset')
        else:
            if username and password:
                user = authenticate(request=request, username=username, password=password)

                if user is not None:
                    login(request, user)
                    if remember_me:
                        request.session.set_expiry(settings.SESSION_REMEMBER_ME_SECONDS)
                    return redirect('home')
                else:
                    messages.error(request, 'Invalid username or password.')
            else:
                messages.error(request, 'Please enter both username and password.')

    return render(request, 'registration/login.html')

def password_reset_request(request):
    if request.method == 'POST':
        username = request.POST.get('reset_username')
        
        if username:
            # Check if the username exists in the database
            user = User.objects.filter(username=username).first()
            if user:
                # Redirect to password reset page
                return redirect('password_reset')
            else:
                # Username does not exist, show a message
                messages.error(request, 'Username does not exist. Please check your email for the username.')
                return redirect('login')
        else:
            # Username not provided, show a message
            messages.warning(request, 'Please enter your username before resetting the password.')
            return redirect('login')

    # If it's not a POST request, just render the login page
    return render(request, 'registration/login.html')

def logout_view(request):
    logout(request)
    # Redirect to the login page after logout
    return redirect('login')

def home(request):
    # Fetch top 5 categories with the most products along with their product count
    top_categories = Category.objects.annotate(num_products=Count('product')).order_by('-num_products')[:5]
    categories_with_product_count = Category.objects.annotate(product_count=Count('product'))

    # Fetch subcategories for the top categories
    categories_with_subcategories = Category.objects.filter(pk__in=top_categories).prefetch_related('subcategory_set')

    # Fetch products containing specific words in their names
    signature_scent_products = Product.objects.filter(tags__icontains='Signature Scent')
    exclusive_offer_products = Product.objects.filter(tags__icontains='Exclusive Offer')
    best_seller_products = Product.objects.filter(tags__icontains='Best Seller')

    # Fetch all banner advertisements
    banner_advertisements = BannerAdvertisement.objects.all()

    context = {
        'categories_with_product_count': categories_with_product_count,
        'categories_with_subcategories': categories_with_subcategories,
        'signature_scent_products': signature_scent_products,
        'exclusive_offer_products': exclusive_offer_products,
        'best_seller_products': best_seller_products,
        'banner_advertisements': banner_advertisements,  # Add banner advertisements to context
    }

    return render(request, 'home.html', context)

def all_products(request):
    # Fetch categories with subcategories
    categories_with_subcategories = Category.objects.prefetch_related('subcategory_set').all()
    
    subcategories = SubCategory.objects.all()

    # Fetch all active products
    all_products = Product.objects.filter(is_active=True)
    
    # Filtering based on category
    category_name = request.GET.get('category')
    if category_name:
        all_products = all_products.filter(categories__name=category_name)
    
    # Filtering based on subcategory
    subcategory_name = request.GET.get('subcategory')
    if subcategory_name:
        all_products = all_products.filter(subcategories__name=subcategory_name)
    
    # Filtering based on price range
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price and max_price:
        all_products = all_products.filter(price__range=(min_price, max_price))
    elif min_price:  # Handle custom price range if only minimum price is provided
        all_products = all_products.filter(price__gte=min_price)
    elif max_price:  # Handle custom price range if only maximum price is provided
        all_products = all_products.filter(price__lte=max_price)
    
    # Filtering based on tags
    tags_query = request.GET.get('tags')
    if tags_query:
        tags_query_list = tags_query.split(',')
        for tag in tags_query_list:
            all_products = all_products.filter(tags__name__icontains=tag.strip())
    
    # Filtering based on average rating
    avg_rating = request.GET.get('avg_rating')
    if avg_rating:
        all_products = all_products.filter(average_rating__gte=avg_rating)
    
    context = {
        'categories_with_subcategories': categories_with_subcategories,
        'subcategories': subcategories,
        'all_products': all_products,
    }
    return render(request, 'all-products.html', context)

def product_detail(request, product_id):
    categories_with_subcategories = Category.objects.prefetch_related('subcategory_set').all()
    product = get_object_or_404(Product, pk=product_id)
    product_images = ProductPhoto.objects.filter(product=product)
    reviews = ProductReview.objects.filter(product=product)
    for review in reviews:
        review.filled_stars = range(review.rating)
        review.empty_stars = range(5 - review.rating)

    # Fetch similar products based on tags or subcategories
    similar_products = Product.objects.filter(
        Q(tags__icontains=product.tags) | Q(subcategories__in=product.subcategories.all())
    ).exclude(id=product_id).distinct()

    context = {
        'categories_with_subcategories': categories_with_subcategories,
        'product': product,
        'product_images': product_images,
        'reviews': reviews,
        'similar_products': similar_products,
    }
    return render(request, 'product_detail.html', context)

@login_required
def submit_review(request, product_id):
    if request.method == 'POST':
        product = Product.objects.get(pk=product_id)
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        user = request.user
        ProductReview.objects.create(product=product, customer=user, rating=rating, comment=comment)
        return redirect('product_detail', product_id=product_id)
    else:
        return redirect('product_detail', product_id=product_id)
        
@login_required
def cart_view(request):
    categories_with_subcategories = Category.objects.prefetch_related('subcategory_set').all()

    user_cart = Cart.objects.filter(user=request.user).first()
    if user_cart:
        cart_items = user_cart.items.all()
    else:
        cart_items = []

    context = {
        'categories_with_subcategories':categories_with_subcategories, 
        'cart_items': cart_items,
        'user_cart':user_cart,
    }
    
    return render(request, 'cart.html', context)


def purchase_product(request, product_id):

    product = get_object_or_404(Product, pk=product_id)

    context = {
        'product':product,
    }
    

    return render(request, 'purchase_product.html', context)


from django.shortcuts import render, redirect
from .models import ShippingAddress, Order, OrderItem, ShippingMethod
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse

from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone

def checkout_view(request):
    if request.method == 'POST':
        # Fetch form data
        email_address = request.POST.get('email-address')
        first_name = request.POST.get('first-name')
        last_name = request.POST.get('last-name')
        address = request.POST.get('address')
        apartment = request.POST.get('apartment')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal-code')
        phone_number = request.POST.get('phone-number')
        delivery_method = request.POST.get('delivery-method')
        product_id = request.POST.get('product_id')
        order_id = request.POST.get('order_id')
        quantity = request.POST.get('quantity')
        total_value = request.POST.get('total_value')

        # Create Shipping Address
        shipping_address = ShippingAddress.objects.create(
            customer=request.user,
            first_name=first_name,
            last_name=last_name,
            address=address,
            apartment=apartment,
            city=city,
            state=state,
            postal_code=postal_code,
            phone_number=phone_number
        )

        # Create or get Order
        if order_id:
            order = Order.objects.get(pk=order_id)
        else:
            order = Order.objects.create(
                user=request.user,
                date_ordered=timezone.now(),
                complete=False,
                is_wholesale_order=False,  # Adjust as needed
                total_price=total_value
            )

        # Create Order Items
        product = Product.objects.get(pk=product_id)
        price = product.price  # Adjust if needed based on wholesale/retail
        OrderItem.objects.create(
            product=product,
            order=order,
            quantity=quantity,  # You might need to adjust this based on your form
            price=price,
            is_wholesale_item=False,
        )

        # Store created objects in session
        request.session['shipping_address'] = shipping_address.id
        request.session['order'] = order.id
        request.session['product'] = product.id
        request.session['order_item'] = OrderItem.objects.filter(order=order).values_list('id', flat=True).first()

        messages.success(request, 'Order placed successfully!')
        return redirect('order_review')  # Redirect to the order review page
    else:
        return render(request, 'purchase_product.html')


from django.shortcuts import render, get_object_or_404
from .models import ShippingAddress, Order, Product, OrderItem
from decimal import Decimal, ROUND_DOWN
from decimal import Decimal

def order_review(request):
    # Retrieve objects from session
    shipping_address_id = request.session.get('shipping_address')
    order_id = request.session.get('order')
    product_id = request.session.get('product')
    order_item_id = request.session.get('order_item')

    # Retrieve objects from database using IDs
    shipping_address = get_object_or_404(ShippingAddress, id=shipping_address_id)
    order = get_object_or_404(Order, id=order_id)
    product = get_object_or_404(Product, id=product_id)
    order_item = get_object_or_404(OrderItem, id=order_item_id)

    # Calculate subtotal
    subtotal = order_item.price * order_item.quantity
    subtotal = subtotal.quantize(Decimal('1'), rounding=ROUND_DOWN)  # Remove decimal digits
    subtotal_formatted = '{:,.0f}'.format(subtotal)

    # Calculate taxes
    taxes = (subtotal * product.tax_percentage) / Decimal(100)
    taxes = taxes.quantize(Decimal('1'), rounding=ROUND_DOWN)  # Remove decimal digits
    taxes_formatted = '{:,.0f}'.format(taxes)

    # Calculate shipping (assuming shipping_price is per product)
    shipping_price = product.shipping_price
    shipping_price = shipping_price.quantize(Decimal('1'), rounding=ROUND_DOWN)  # Remove decimal digits
    shipping_price_formatted = '{:,.0f}'.format(shipping_price)

    # Calculate total price
    total_price = subtotal + taxes + shipping_price
    total_price = total_price.quantize(Decimal('1'), rounding=ROUND_DOWN)  # Remove decimal digits
    total_price_formatted = '{:,.0f}'.format(total_price)

            # Create a context dictionary
    context = {
        'shipping_address': shipping_address,
        'order': order,
        'product': product,
        'order_item': order_item,
        'subtotal_formatted': subtotal_formatted,
        'taxes_formatted': taxes_formatted,
        'shipping_price_formatted': shipping_price_formatted,
        'total_price_formatted': total_price_formatted,
    }

    return render(request, 'order_review.html', context)

from django.shortcuts import render

def customer_support(request):
    # You can pass any additional context data you want to display on the page
    return render(request, 'customer_support.html', {})

from django.shortcuts import render

def terms_of_service(request):
    return render(request, 'terms_of_service.html', {})

from django.shortcuts import render

def privacy_policy(request):
    return render(request, 'privacy_policy.html', {})

from django.shortcuts import render

def cancellation_refund_policy(request):
    return render(request, 'cancellation_refund_policy.html', {})
