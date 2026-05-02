from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Exists, OuterRef, Q, Sum
from django.utils import timezone
from .models import Artwork, Category, Cart, Order, Review, Wishlist, WishlistItem, OrderItem
from .forms import ArtworkForm


def build_seller_notifications(user):
    today = timezone.localdate()

    sales_today = OrderItem.objects.filter(
        seller=user,
        order__created_at__date=today
    ).select_related('artwork', 'order').order_by('-order__created_at')

    wishlist_events = WishlistItem.objects.filter(
        artwork__seller=user,
        created_at__date=today
    ).select_related('artwork').order_by('-created_at')

    notifications = []

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


# ================= GALLERY =================
def gallery_list(request):
    # ✅ Show only available items
    artworks = Artwork.objects.filter(status='available')
    categories = Category.objects.all()

    category = request.GET.get('category')
    if category:
        artworks = artworks.filter(category__id=category)

    return render(request, 'gallery/gallery_list.html', {
        'artworks': artworks,
        'categories': categories,
    })


def artwork_detail(request, pk):
    artwork = get_object_or_404(
        Artwork.objects.select_related('category', 'seller', 'seller__profile'),
        pk=pk
    )
    artwork.views += 1
    artwork.save(update_fields=['views'])
    reviews = artwork.reviews.select_related('reviewer').all()
    author_profile = getattr(artwork.seller, 'profile', None)
    artist_queryset = Artwork.objects.filter(seller=artwork.seller)
    artist_artwork_count = artist_queryset.count()
    artist_available_count = artist_queryset.filter(status='available').count()
    artist_total_views = artist_queryset.aggregate(total_views=Sum('views'))['total_views'] or 0

    return render(request, 'gallery/artwork_detail.html', {
        'artwork': artwork,
        'reviews': reviews,
        'author_profile': author_profile,
        'artist_artwork_count': artist_artwork_count,
        'artist_available_count': artist_available_count,
        'artist_total_views': artist_total_views,
    })


# ================= SELLER DASHBOARD =================
@login_required
def seller_dashboard(request):
    profile = getattr(request.user, 'profile', None)

    seller_artworks = Artwork.objects.filter(
        seller=request.user
    ).annotate(
        is_sold=Exists(OrderItem.objects.filter(artwork_id=OuterRef('pk')))
    )

    available_artworks = seller_artworks.filter(
        status='available',
        is_sold=False
    )

    sold_artworks = seller_artworks.filter(
        Q(status='sold') | Q(is_sold=True)
    )

    pending_artworks = Artwork.objects.filter(
        seller=request.user,
        status='pending'
    )

    recent_sales = OrderItem.objects.filter(
        seller=request.user
    ).select_related('order', 'artwork')

    seller_notifications = build_seller_notifications(request.user)

    return render(request, 'users/seller_dashboard.html', {
        'profile': profile,
        'available_artworks': available_artworks,
        'sold_artworks': sold_artworks,
        'pending_artworks': pending_artworks,
        'recent_sales': recent_sales,
        'seller_notifications': seller_notifications,
    })


# ================= CART =================
@login_required
def add_to_cart(request, pk):
    artwork = get_object_or_404(Artwork, pk=pk)

    # ❌ Prevent adding sold items
    if artwork.status == 'sold' or OrderItem.objects.filter(artwork=artwork).exists():
        messages.error(request, 'This item is already sold!')
        return redirect('gallery:gallery_list')

    cart, _ = Cart.objects.get_or_create(user=request.user)

    from .models import CartItem
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        artwork=artwork,
        defaults={'quantity': 1}
    )

    if not created:
        messages.info(request, f'{artwork.title} is already in your cart!')
        return redirect('gallery:cart')

    messages.success(request, f'{artwork.title} added to cart!')
    return redirect('gallery:cart')


@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return render(request, 'gallery/cart.html', {'cart': cart})


@login_required
def remove_from_cart(request, item_id):
    from .models import CartItem
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed!')
    return redirect('gallery:cart')


# ================= WISHLIST =================
@login_required
def add_to_wishlist(request, pk):
    artwork = get_object_or_404(Artwork, pk=pk)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    wishlist_item = WishlistItem.objects.filter(wishlist=wishlist, artwork=artwork).first()

    if wishlist_item:
        wishlist_item.delete()
        wishlist.artworks.remove(artwork)
        added = False
    else:
        WishlistItem.objects.create(wishlist=wishlist, artwork=artwork)
        wishlist.artworks.add(artwork)
        added = True

    wishlist.save(update_fields=['updated_at'])

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'added': added})

    return redirect('gallery:artwork_detail', pk=pk)


@login_required
def wishlist_view(request):
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    return render(request, 'gallery/wishlist.html', {'wishlist': wishlist})


# ================= CHECKOUT =================
@login_required
def checkout(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        artwork_ids = []
        seen_ids = set()

        for raw_id in request.POST.getlist('artwork_ids'):
            try:
                artwork_id = int(raw_id)
            except (TypeError, ValueError):
                continue

            if artwork_id not in seen_ids:
                seen_ids.add(artwork_id)
                artwork_ids.append(artwork_id)

        if artwork_ids:
            artworks = list(Artwork.objects.filter(id__in=artwork_ids).select_related('seller'))
            purchasable_artworks = [
                artwork for artwork in artworks
                if artwork.status != 'sold' and not OrderItem.objects.filter(artwork=artwork).exists()
            ]

            if not purchasable_artworks:
                messages.error(request, 'These artworks are already sold out.')
                return redirect('buyer')

            total_amount = sum(artwork.price for artwork in purchasable_artworks)
            order = Order.objects.create(
                buyer=request.user,
                total_amount=total_amount
            )

            for artwork in purchasable_artworks:
                OrderItem.objects.create(
                    order=order,
                    artwork=artwork,
                    seller=artwork.seller,
                    quantity=1,
                    price=artwork.price
                )
                artwork.status = 'sold'
                artwork.save(update_fields=['status', 'updated_at'])

            messages.success(request, 'Order placed successfully!')
            return redirect('buyer')

        order = Order.objects.create(
            buyer=request.user,
            total_amount=cart.get_total()
        )

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                artwork=item.artwork,
                seller=item.artwork.seller,
                quantity=item.quantity,
                price=item.artwork.price
            )

            # ✅ MAIN FIX: mark as SOLD
            item.artwork.status = 'sold'
            item.artwork.save()

        # ✅ Clear cart
        cart.items.all().delete()

        messages.success(request, 'Order placed successfully!')

        # ❌ REMOVED order_detail redirect
        return redirect('buyer')

    return render(request, 'gallery/checkout.html', {'cart': cart})


# ================= REVIEW =================
@login_required
def add_review(request, pk):
    artwork = get_object_or_404(Artwork, pk=pk)

    if request.method == 'POST':
        Review.objects.update_or_create(
            artwork=artwork,
            reviewer=request.user,
            defaults={
                'rating': request.POST.get('rating'),
                'comment': request.POST.get('comment')
            }
        )

    return redirect('gallery:artwork_detail', pk=pk)


# ================= ADD ARTWORK =================
@login_required
def add_artwork(request):
    if request.method == 'POST':
        form = ArtworkForm(request.POST, request.FILES)
        if form.is_valid():
            artwork = form.save(commit=False)
            artwork.seller = request.user
            artwork.save()
            messages.success(request, 'Artwork uploaded!')
            return redirect('seller')
    else:
        form = ArtworkForm()

    return render(request, 'gallery/add_artwork.html', {'form': form})

# ================= EDIT / DELETE ARTWORK =================
@login_required
def edit_artwork(request, pk):
    artwork = get_object_or_404(Artwork, pk=pk, seller=request.user)
    if request.method == 'POST':
        form = ArtworkForm(request.POST, request.FILES, instance=artwork)
        if form.is_valid():
            form.save()
            messages.success(request, 'Artwork updated successfully!')
            return redirect('seller')
    else:
        form = ArtworkForm(instance=artwork)

    return render(request, 'gallery/edit_artwork.html', {'form': form, 'artwork': artwork})


@login_required
def delete_artwork(request, pk):
    artwork = get_object_or_404(Artwork, pk=pk, seller=request.user)
    if request.method == 'POST':
        artwork.delete()
        messages.success(request, 'Artwork deleted successfully!')
    return redirect('seller')


# ================= TESTIMONIAL =================
@login_required
def submit_testimonial(request):
    if request.method == 'POST':
        from .models import Testimonial
        rating = request.POST.get('rating', 5)
        comment = request.POST.get('comment', '')
        
        referer = request.META.get('HTTP_REFERER', '')
        if 'seller' in referer.lower():
            role = 'seller'
        elif 'buyer' in referer.lower():
            role = 'buyer'
        else:
            try:
                role = request.user.profile.role
            except Exception:
                role = 'buyer'
        
        Testimonial.objects.create(
            user=request.user,
            role_at_time=role,
            rating=int(rating),
            comment=comment
        )
        messages.success(request, 'Your testimonial has been submitted!')
        
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def edit_testimonial(request, pk):
    from .models import Testimonial
    testimonial = get_object_or_404(Testimonial, pk=pk, user=request.user)
    if request.method == 'POST':
        testimonial.rating = int(request.POST.get('rating', 5))
        testimonial.comment = request.POST.get('comment', '')
        testimonial.save()
        messages.success(request, 'Your review has been updated!')
        return redirect(request.session.get('last_dashboard', 'home'))
    
    request.session['last_dashboard'] = request.META.get('HTTP_REFERER', 'home')
    return render(request, 'gallery/edit_testimonial.html', {'testimonial': testimonial})

@login_required
def delete_testimonial(request, pk):
    from .models import Testimonial
    testimonial = get_object_or_404(Testimonial, pk=pk, user=request.user)
    if request.method == 'POST':
        testimonial.delete()
        messages.success(request, 'Your review has been deleted.')
    return redirect(request.META.get('HTTP_REFERER', 'home'))
