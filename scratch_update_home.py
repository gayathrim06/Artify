import os

path = r'c:\Users\91894\OneDrive\Desktop\AWT\art_gallery\art_gallery\views.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

target = '''def home(request):
    from gallery.models import Artwork'''
replacement = '''def home(request):
    from gallery.models import Artwork, Testimonial
    try:
        testimonials = Testimonial.objects.all().order_by('-created_at')[:10]
    except:
        testimonials = []
'''

if target in content:
    content = content.replace(target, replacement)
    
target2 = '''return render(request, 'users/home.html', {'featured_artworks': featured_artworks})'''
replacement2 = '''return render(request, 'users/home.html', {'featured_artworks': featured_artworks, 'testimonials': testimonials})'''

if target2 in content:
    content = content.replace(target2, replacement2)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
