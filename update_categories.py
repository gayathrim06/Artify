import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'art_gallery.settings')
django.setup()

from gallery.models import Category

# Clean up and add requested categories
Category.objects.filter(name='Sculpture').delete()
Category.objects.get_or_create(name='Painting')
Category.objects.get_or_create(name='Pottery')
Category.objects.get_or_create(name='Plate Design')
Category.objects.get_or_create(name='Digital Art')

print("Categories updated successfully!")
