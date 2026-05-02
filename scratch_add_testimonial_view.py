import os
import sys

path = r'c:\Users\91894\OneDrive\Desktop\AWT\art_gallery\gallery\views.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

view_code = '''
# ================= TESTIMONIAL =================
@login_required
def submit_testimonial(request):
    if request.method == 'POST':
        from .models import Testimonial
        rating = request.POST.get('rating', 5)
        comment = request.POST.get('comment', '')
        
        # Determine role at time
        role = getattr(request.user.profile, 'role', 'buyer')
        
        Testimonial.objects.create(
            user=request.user,
            role_at_time=role,
            rating=int(rating),
            comment=comment
        )
        messages.success(request, 'Your testimonial has been submitted!')
        
    return redirect('home')
'''
if 'def submit_testimonial' not in content:
    content = content + '\n' + view_code

# Also update home view to pass testimonials
if 'def home(request):' in content:
    target = '''def home(request):
    from gallery.models import Artwork'''
    replacement = '''def home(request):
    from gallery.models import Artwork, Testimonial
    testimonials = Testimonial.objects.all().order_by('-created_at')[:10]'''
    content = content.replace(target, replacement)
    
    target2 = '''return render(request, 'users/home.html', {'featured_artworks': featured_artworks})'''
    replacement2 = '''return render(request, 'users/home.html', {'featured_artworks': featured_artworks, 'testimonials': testimonials})'''
    content = content.replace(target2, replacement2)


with open(path, 'w', encoding='utf-8') as f:
    f.write(content)


# URL update
url_path = r'c:\Users\91894\OneDrive\Desktop\AWT\art_gallery\gallery\urls.py'
with open(url_path, 'r', encoding='utf-8') as f:
    url_content = f.read()

if 'submit_testimonial' not in url_content:
    url_content = url_content.replace('urlpatterns = [', "urlpatterns = [\n    path('submit-testimonial/', views.submit_testimonial, name='submit_testimonial'),")

with open(url_path, 'w', encoding='utf-8') as f:
    f.write(url_content)

