import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'art_gallery.settings')
django.setup()

from django.contrib.auth.models import User

# Remove if exists and recreate
User.objects.filter(username='root').delete()
User.objects.create_superuser('root', 'admin@example.com', 'admin123')

print("Admin 'root' created successfully!")
