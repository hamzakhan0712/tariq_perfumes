from django.urls import path
from .views import signup,home,cart_view, customer_support, cancellation_refund_policy, terms_of_service, privacy_policy, order_review, product_detail, checkout_view, submit_review, purchase_product, login_view, logout_view,password_reset_request,error_404,error_500,offline_view,all_products
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', home, name='home'),  # URL pattern for the home page
    path('404/', error_404, name='error_404'),
    path('500/', error_500, name='error_500'),
    path('offline/', offline_view, name='offline'),

   path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        html_email_template_name='registration/password_reset_email.html',
        success_url='/password_reset/done/'
    ), name='password_reset'),

    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url='/reset/done/'
    ), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),

    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('password_reset_request/', password_reset_request, name='password_reset_request'),
    path('all_products', all_products, name='all_products'),
    path('product/<int:product_id>/', product_detail, name='product_detail'),
    path('product/<int:product_id>/submit_review/', submit_review, name='submit_review'),
    path('product/<int:product_id>/purchase/', purchase_product, name='purchase_product'),
    path('cart/', cart_view, name='cart'),
    path('checkout/', checkout_view, name='checkout'),
    path('order-review/', order_review, name='order_review'),
    path('customer-support/', customer_support, name='customer_support'),
    path('terms-of-service/', terms_of_service, name='terms_of_service'),
    path('privacy-policy/', privacy_policy, name='privacy_policy'),
    path('cancellation-refund-policy/', cancellation_refund_policy, name='cancellation_refund_policy')

]
