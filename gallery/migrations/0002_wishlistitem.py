from django.db import migrations, models
import django.db.models.deletion


def copy_existing_wishlist_items(apps, schema_editor):
    Wishlist = apps.get_model('gallery', 'Wishlist')
    WishlistItem = apps.get_model('gallery', 'WishlistItem')

    for wishlist in Wishlist.objects.all():
        for artwork in wishlist.artworks.all():
            WishlistItem.objects.get_or_create(
                wishlist=wishlist,
                artwork=artwork,
            )


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WishlistItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('artwork', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wishlist_items', to='gallery.artwork')),
                ('wishlist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='gallery.wishlist')),
            ],
            options={
                'ordering': ['-created_at'],
                'unique_together': {('wishlist', 'artwork')},
            },
        ),
        migrations.RunPython(copy_existing_wishlist_items, migrations.RunPython.noop),
    ]
