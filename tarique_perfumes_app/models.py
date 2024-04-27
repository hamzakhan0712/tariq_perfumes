from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name
    
class SubCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price= models.DecimalField(max_digits=10, decimal_places=2)
    previous_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    quantity = models.CharField(max_length=50)
    tags = models.TextField()
    main_image_url = models.URLField(null=True, blank=True)
    categories = models.ManyToManyField(Category)
    subcategories = models.ManyToManyField(SubCategory)
    in_stock_retail = models.BooleanField(default=True)
    in_stock_wholesale = models.BooleanField(default=True)
    sku = models.CharField(max_length=100)
    unit = models.CharField(max_length=50)
    manufacturing_date = models.DateField()
    expiry_date = models.DateField()
    is_active = models.BooleanField(default=True)
    average_rating = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    shipping_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.name
    
class ProductPhoto(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image_url = models.URLField()

    def __str__(self):
        return f"Photo of {self.product.name}"

class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_reviews')
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.customer.username} for {self.product.name}"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    is_wholesale_order = models.BooleanField(default=False)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0,null=True)

    def __str__(self):
        return f"Order #{self.id}"

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_wholesale_item = models.BooleanField(default=False)


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    items = models.ManyToManyField(OrderItem)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart for {self.user.username}"



class OrderHistory(models.Model):
    ORDER_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled')
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='history')
    status = models.CharField(max_length=100, choices=ORDER_STATUS_CHOICES, default='Pending')
    notes = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.order.id} - {self.status}"

class Inventory(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='inventory')
    stock_level_retail = models.PositiveIntegerField(default=0)
    stock_level_wholesale = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Inventory for {self.product.name}"

class ShippingMethod(models.Model):
    STANDARD_DELIVERY = 'Standard Delivery'
    EXPRESS_DELIVERY = 'Express Delivery'

    DELIVERY_CHOICES = [
        (STANDARD_DELIVERY, 'Standard Delivery (4-10 business days)'),
        (EXPRESS_DELIVERY, 'Express Delivery (2-5 business days)'),
    ]

    name = models.CharField(max_length=100, choices=DELIVERY_CHOICES, default=STANDARD_DELIVERY)
    description = models.TextField()
    cost_retail = models.DecimalField(max_digits=10, decimal_places=2)
    cost_wholesale = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_delivery_time = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class PaymentMethod(models.Model):
    PAYMENT_OPTIONS = [
        ('card', 'Pay with Card'),
        ('cash_on_delivery', 'Cash on Delivery'),
        ('gpay', 'G-Pay'),
        ('phone_pay', 'Phone Pay'),
        # Add more payment options as needed
    ]
    name = models.CharField(max_length=100, choices=PAYMENT_OPTIONS)

    def __str__(self):
        return self.get_name_display()

class ShippingAddress(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100,null=True)
    last_name = models.CharField(max_length=100,null=True)
    address = models.TextField()
    apartment = models.CharField(max_length=100,null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, validators=[RegexValidator(regex='^[0-9]{5}$', message='Enter a valid postal code.')])
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return f"Shipping address for {self.customer.username}"


class Invoice(models.Model):
    ORDER_STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Waiting', 'Waiting'),
        ('Unpaid', 'Unpaid')
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    issued_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    payment_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='Unpaid')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True)
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.CASCADE,default=1)
    transaction_id = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Invoice #{self.id} for Order #{self.order.id}"

class Payment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE,default=1)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100)
    payment_date = models.DateTimeField(auto_now_add=True)
    is_successful = models.BooleanField(default=False)

    def __str__(self):
        return f"Payment for Invoice #{self.invoice.id}"

class Promotion(models.Model):
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    discount_amount_retail = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount_wholesale = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self):
        return self.code

class DiscountCoupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()

    def __str__(self):
        return self.code

class DiscountRule(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    minimum_order_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    applicable_categories = models.ManyToManyField(Category)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name

class Feedback(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    message = models.TextField()
    rating = models.PositiveSmallIntegerField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.customer.username}"

class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscription_date = models.DateTimeField(auto_now_add=True)
    is_subscribed = models.BooleanField(default=True)

    def __str__(self):
        return self.email

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    publish_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name}"
 
class BannerAdvertisement(models.Model):
    name = models.CharField(max_length=100, default="N/A")
    description = models.TextField(blank=True, null=True)
    image_url = models.URLField()

    def __str__(self):
        return self.name

class FAQ(models.Model):
    question = models.CharField(max_length=200)
    answer = models.TextField()

    def __str__(self):
        return self.question

class ReturnRequest(models.Model):
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')])
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Return request for {self.order_item.product.name}"

class GiftCard(models.Model):
    code = models.CharField(max_length=20, unique=True)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

class Wishlist(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)

    def __str__(self):
        return f"Wishlist for {self.customer.username}"

class Refund(models.Model):
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    amount_refunded = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    processed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Refund for {self.order_item.product.name}"




























