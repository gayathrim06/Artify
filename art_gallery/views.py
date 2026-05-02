from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Exists, OuterRef, Q
from django.utils import timezone


def build_seller_notifications(user):
    from gallery.models import OrderItem, WishlistItem

    today = timezone.localdate()
    notifications = []

    sales_today = OrderItem.objects.filter(
        seller=user,
        order__created_at__date=today
    ).select_related('artwork', 'order').order_by('-order__created_at')

    wishlist_events = WishlistItem.objects.filter(
        artwork__seller=user,
        created_at__date=today
    ).select_related('artwork').order_by('-created_at')

    for sale in sales_today:
        if sale.artwork:
            notifications.append({
                'type': 'sale',
                'title': 'Artwork Sold',
                'message': f'Your artwork "{sale.artwork.title}" was sold today.',
                'created_at': sale.order.created_at,
            })

    for event in wishlist_events:
        notifications.append({
            'type': 'wishlist',
            'title': 'Wishlist Update',
            'message': f'Someone added your artwork "{event.artwork.title}" to their wishlist.',
            'created_at': event.created_at,
        })

    notifications.sort(key=lambda item: item['created_at'], reverse=True)
    return notifications

# ---------------- ADMIN ----------------

def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect('dashboard')

    return render(request, 'custom_admin/login.html')

@login_required
def dashboard(request):
    if not request.user.is_superuser:
        return redirect('home')
        
    from django.contrib.auth.models import User
    from gallery.models import Artwork, Order, Testimonial
    
    total_users = User.objects.exclude(is_superuser=True).count()
    total_artworks = Artwork.objects.count()
    total_orders = Order.objects.count()
    
    recent_artworks = Artwork.objects.select_related('seller').order_by('-created_at')[:10]
    recent_orders = Order.objects.select_related('buyer').order_by('-created_at')[:10]
    
    testimonials = Testimonial.objects.select_related('user').order_by('-created_at')
    
    context = {
        'total_users': total_users,
        'total_artworks': total_artworks,
        'total_orders': total_orders,
        'recent_artworks': recent_artworks,
        'recent_orders': recent_orders,
        'testimonials': testimonials,
    }
    return render(request, 'custom_admin/dashboard.html', context)

@login_required
def admin_reply_testimonial(request, pk):
    if not request.user.is_superuser:
        return redirect('home')
        
    from gallery.models import Testimonial
    from django.shortcuts import get_object_or_404
    from django.contrib import messages
    
    testimonial = get_object_or_404(Testimonial, pk=pk)
    
    if request.method == 'POST':
        admin_reply = request.POST.get('admin_reply', '').strip()
        testimonial.admin_reply = admin_reply
        testimonial.save()
        messages.success(request, 'Reply saved successfully.')
        
    return redirect('dashboard')


# ---------------- USER ----------------

def home(request):
    from gallery.models import Artwork, Testimonial
    try:
        testimonials = list(Testimonial.objects.all().order_by('-created_at')[:10])
    except:
        testimonials = []

    featured_artworks = Artwork.objects.all().order_by('-created_at')[:6]
    return render(request, 'users/home.html', {'featured_artworks': featured_artworks, 'testimonials': testimonials})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            request.session['show_login_welcome'] = True

            if user.is_superuser:
                return redirect('dashboard')
            elif hasattr(user, 'profile') and user.profile.role == 'seller':
                return redirect('seller')
            elif user.is_staff: # Fallback for old seller logic
                return redirect('seller')
            else:
                return redirect('buyer')

    return render(request, 'users/login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        role = request.POST['role']
        password = request.POST['password']
        password2 = request.POST['password2']
        
        if password != password2:
            messages.error(request, 'Passwords do not match')
            return redirect('register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('register')
        
        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        
        if role == 'seller':
            user.is_staff = True
            user.save()
        
        return redirect('login')
    
    return render(request, 'users/register.html')

@login_required
def buyer_dashboard(request):
    from gallery.models import Artwork, OrderItem, Wishlist
    artworks = Artwork.objects.select_related('category', 'seller', 'seller__profile').annotate(
        is_sold=Exists(OrderItem.objects.filter(artwork_id=OuterRef('pk')))
    ).order_by('-created_at')
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    wishlist_artworks = wishlist.artworks.select_related('seller', 'seller__profile').annotate(
        is_sold=Exists(OrderItem.objects.filter(artwork_id=OuterRef('pk')))
    )
    show_login_welcome = request.session.pop('show_login_welcome', False)
    
    from gallery.models import Testimonial
    user_testimonials = Testimonial.objects.filter(user=request.user).order_by('-created_at')
    
    wishlist_payload = [
        {
            'id': artwork.id,
            'title': artwork.title,
            'price': str(artwork.price),
            'image_url': artwork.image.url if artwork.image else '',
            'is_available': artwork.status == 'available' and not getattr(artwork, 'is_sold', False),
        }
        for artwork in wishlist_artworks
    ]
    return render(request, 'users/buyer_dashboard.html', {
        'artworks': artworks,
        'wishlist_artworks': wishlist_artworks,
        'wishlist_artwork_ids': list(wishlist_artworks.values_list('id', flat=True)),
        'wishlist_payload': wishlist_payload,
        'show_login_welcome': show_login_welcome,
        'user_testimonials': user_testimonials,
    })

@login_required
def seller_dashboard(request):
    from gallery.models import Artwork, OrderItem, UserProfile
    
    user = request.user
    
    # Grab or initialize user profile info
    try:
        profile = user.profile
    except:
        profile = None
    
    seller_artworks = Artwork.objects.filter(seller=user).annotate(
        is_sold=Exists(OrderItem.objects.filter(artwork_id=OuterRef('pk')))
    )

    # Seller's artworks
    available_artworks = seller_artworks.filter(status='available', is_sold=False)
    sold_artworks = seller_artworks.filter(Q(status='sold') | Q(is_sold=True))
    
    # Recent Buyers (Orders from the seller)
    recent_sales = OrderItem.objects.filter(seller=user).select_related('order', 'order__buyer', 'artwork').order_by('-order__created_at')
    seller_notifications = build_seller_notifications(user)
    
    from gallery.models import Testimonial
    user_testimonials = Testimonial.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'profile': profile,
        'available_artworks': available_artworks,
        'sold_artworks': sold_artworks,
        'recent_sales': recent_sales,
        'seller_notifications': seller_notifications,
        'user_testimonials': user_testimonials,
    }
    
    return render(request, 'users/seller_dashboard.html', context)

def logout_view(request):
    logout(request)
    return redirect('home')

