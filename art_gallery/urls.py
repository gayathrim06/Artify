from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from gallery import views as gallery_views   # ✅ IMPORTANT

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),

    # Gallery app
    path('gallery/', include('gallery.urls')),

    # Custom admin
    path('admin-login/', views.admin_login, name='admin_login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-reply/<int:pk>/', views.admin_reply_testimonial, name='admin_reply_testimonial'),

    # User pages
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),

    path('buyer/', views.buyer_dashboard, name='buyer'),

    # ✅ FIXED LINE (correct source)
    path('buyer-checkout/', gallery_views.checkout, name='buyer_checkout'),

    path('seller/', views.seller_dashboard, name='seller'),
    path('logout/', views.logout_view, name='logout'),
    path('api/artist/<str:username>/', views.artist_details_api, name='artist_details_api'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)