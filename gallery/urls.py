from django.urls import path
from . import views

app_name = 'gallery'

urlpatterns = [
    path('submit-testimonial/', views.submit_testimonial, name='submit_testimonial'),
    path('testimonial/<int:pk>/edit/', views.edit_testimonial, name='edit_testimonial'),
    path('testimonial/<int:pk>/delete/', views.delete_testimonial, name='delete_testimonial'),
    path('', views.gallery_list, name='gallery_list'),

    # Artwork
    path('add/', views.add_artwork, name='add_artwork'),
    path('artwork/<int:pk>/', views.artwork_detail, name='artwork_detail'),
    path('artwork/<int:pk>/edit/', views.edit_artwork, name='edit_artwork'),
    path('artwork/<int:pk>/delete/', views.delete_artwork, name='delete_artwork'),

    # Cart
    path('add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    # Wishlist
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('add-to-wishlist/<int:pk>/', views.add_to_wishlist, name='add_to_wishlist'),

    # Checkout
    path('checkout/', views.checkout, name='checkout'),
    

    # Reviews
    path('review/<int:pk>/', views.add_review, name='add_review'),
    
    # Profile
    path('profile/edit/', views.edit_profile, name='edit_profile'),
]