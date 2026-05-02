from django.test import TestCase
from django.contrib.auth.models import User
from .models import Artwork, Category, Order


class ArtworkTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.category = Category.objects.create(name='Abstract')
        self.artwork = Artwork.objects.create(
            seller=self.user,
            title='Test Artwork',
            description='Test description',
            category=self.category,
            price=100.00,
            image='test.jpg'
        )
    
    def test_artwork_creation(self):
        self.assertEqual(self.artwork.title, 'Test Artwork')
        self.assertEqual(self.artwork.status, 'available')
