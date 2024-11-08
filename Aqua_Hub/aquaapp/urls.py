"""
URL configuration for Aqua_Hub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . views import *

urlpatterns = [
    path('',index_view, name='index'),
     path('login',login_view, name='login'),
      path('slogin',seller_login, name='slogin'),
      path('userreg',user_reg, name='userreg'),
      path('admin' ,admin_view, name='admin'),
      path('sellereg',seller_reg, name='sellereg'),
      path('userhome',user_home, name='userhome'),
      path('sellerdash',seller_dash, name='sellerdash'),
      path('logout',logout_view, name='logout'),
      path('approve',admin_approv,name='approve'),
      path('adminappr/<int:id>',approve_seller,name='approve_seller'),
      path('sellerappr',approved_seller,name='sellerappr'),
      path('forgotpassword',forgot_password,name='forgotpassword'),
      path('reset_password/<uidb64>/<token>/', reset_password, name='reset_password'),
      path('removeseller/<int:seller_id>',remove_seller,name='removeseller'),
      path('add_product/',add_product, name='add_product'),
      path('about',about_view, name='about'),
      path('sellerproduct/',seller_product, name='sellerproduct'),
      path('oauth/', include('social_django.urls', namespace='social')),
      path('edit_product/<int:product_id>',edit_view,name='edit_product'),
      path('prouct_list/',product_list_view,name='product_list'),
      path('product/<int:product_id>/',product_detail, name='product_detail'),
      path('add_to_cart/<int:product_id>/',add_to_cart, name='add_to_cart'),
      path('book_now/<int:product_id>/',book_now, name='book_now'),
      path('cart/', view_cart, name='view_cart'),
      path('remove_from_cart/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
      path('disable_product/<int:product_id>/',disable_product, name='disable_product'),
      path('enable_product/<int:product_id>/',enable_product, name='enable_product'),
      path('profile/', profile_view, name='Profile'),
      path('sprofile/',edit_seller_profile, name='sprofile'),
      path('virtual-tank/', view_virtual_tank, name='virtual_tank_view'),
      path('create-tank/', create_virtual_tank, name='create_virtual_tank'),
      path('blogs/', blog_list, name='blog_list'),
      path('blogs/<int:pk>/', blog_detail, name='blog_detail'),
      path('blogs/create/', create_blog, name='create_blog'),
      path('blog/<int:blog_id>/comment/', add_comment, name='add_comment'),
      path('myblogs/', my_blogs, name='my_blogs'),
      path('blogs/<int:blog_id>/edit/', edit_blog, name='edit_blog'),
      path('reject_seller/<int:seller_id>/', reject_seller, name='reject_seller'),
      path('manage-users/', manage_users, name='manage_users'),
      path('complaints/register/', register_complaint, name='register_complaint'),
      path('view-complaints/', view_complaints, name='view_complaints'),
      path('product/<int:product_id>/book-now/<int:quantity>', book_now, name='book_now'),
      path('product/<int:product_id>/enter-address/', add_new_address, name='add_new_address'),
      path('product/<int:product_id>/book-now/', create_order, name='order_now'),
      path('payment-handler/', payment_handler, name='payment_handler'),
      path('completed-orders/', completed_orders, name='completed_orders'),
      path('seller/orders/', seller_orders, name='seller_orders'),
      path('admin_orders/', admin_all_orders, name='admin_all_orders'),
      path('product/<int:product_id>/select-address/', select_address, name='select_address'),
       path('reply-complaint/<int:complaint_id>/', reply_complaint, name='reply_complaint'),
      



      
      
     
    
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)