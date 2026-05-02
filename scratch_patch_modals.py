import os
import re

home_path = r'c:\Users\91894\OneDrive\Desktop\AWT\art_gallery\templates\users\home.html'
buyer_path = r'c:\Users\91894\OneDrive\Desktop\AWT\art_gallery\templates\users\buyer_dashboard.html'

def patch_file(path, replacements):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        for target, replacement in replacements:
            content = content.replace(target, replacement)
            # handle windows line endings just in case
            content = content.replace(target.replace('\n', '\r\n'), replacement.replace('\n', '\r\n'))
            
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

# 1. ADD TESTIMONIALS TO HOME
testimonial_html = '''    <!-- TESTIMONIALS SECTION -->
    <section class="section" id="testimonials" style="background: #0a0a0a;">
        <h2 class="section-title">What They <span>Say</span></h2>
        <div style="display: flex; gap: 20px; overflow-x: auto; padding-bottom: 20px;">
            {% for review in testimonials %}
            <div style="min-width: 300px; background: rgba(255,255,255,0.05); padding: 25px; border-radius: 15px; border: 1px solid var(--glass-border);">
                <div style="color: var(--primary); font-size: 20px; margin-bottom: 15px;">
                    {% if review.rating == 5 %}⭐⭐⭐⭐⭐{% elif review.rating == 4 %}⭐⭐⭐⭐{% elif review.rating == 3 %}⭐⭐⭐{% elif review.rating == 2 %}⭐⭐{% else %}⭐{% endif %}
                </div>
                <p style="color: var(--text-main); font-size: 16px; margin-bottom: 20px; font-style: italic;">"{{ review.comment }}"</p>
                <div style="font-size: 14px; color: var(--text-muted);">
                    <strong style="color: #fff;">{{ review.user.username }}</strong><br>
                    <span style="text-transform: capitalize;">{{ review.role_at_time }}</span>
                </div>
                {% if review.admin_reply %}
                <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.05); font-size: 13px; color: var(--primary);">
                    <strong>Artify Response:</strong><br>
                    {{ review.admin_reply }}
                </div>
                {% endif %}
            </div>
            {% empty %}
            <p style="color: var(--text-muted); text-align: center; width: 100%;">No testimonials yet. Join us and leave the first!</p>
            {% endfor %}
        </div>
    </section>

    <!-- CALL TO ACTION -->'''

# 2. HANGING FRAME CSS
old_css = '''        .modal-content {
            background: rgba(20, 20, 20, 0.95);
            margin: auto;'''

new_css = '''        /* WALLPAPER BACKGROUND */
        .artwork-modal {
            background: radial-gradient(circle at center, #2a2a2a, #000);
        }

        .modal-content {
            /* PLAIN WALL TEXTURE */
            background: #e8e6e1 url('https://www.transparenttextures.com/patterns/cream-paper.png');
            margin: auto;'''

old_frame_css = '''        .modal-frame {
            flex: 1;
            padding: 20px;
            background: #111;
            /* GOLDEN FRAME EFFECT */
            border: 24px solid transparent;
            border-image: linear-gradient(to bottom right, #e6c55d, #b38b22, #ffe58f, #8a6314) 1;
            box-shadow: inset 0 0 20px rgba(0,0,0,0.8), 0 20px 40px rgba(0,0,0,0.6);
            display: flex;
            align-items: center;
            justify-content: center;
        }'''

new_frame_css = '''        /* HANGING STRING EFFECT */
        .hanging-string {
            position: absolute;
            top: -40px;
            left: 50%;
            width: 100px;
            height: 40px;
            border-left: 2px solid #555;
            border-right: 2px solid #555;
            transform: translateX(-50%);
            clip-path: polygon(50% 0, 100% 100%, 0 100%);
        }
        .hanging-nail {
            position: absolute;
            top: -45px;
            left: 50%;
            width: 10px;
            height: 10px;
            background: radial-gradient(circle, #333, #000);
            border-radius: 50%;
            transform: translateX(-50%);
            box-shadow: 0 2px 5px rgba(0,0,0,0.5);
        }

        .modal-frame {
            flex: 1;
            padding: 30px;
            background: #fff; /* White matting */
            /* WOODEN/GOLDEN FRAME EFFECT */
            border: 30px solid #4a2e15;
            border-image: linear-gradient(to bottom right, #5c3a21, #2b180d, #5c3a21) 1;
            box-shadow: inset 0 0 15px rgba(0,0,0,0.5), 0 30px 50px rgba(0,0,0,0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }'''

hook_html_old = '''            <div class="modal-frame">
                <img id="modalImage" src="" alt="Artwork">
            </div>'''
hook_html_new = '''            <div class="modal-frame">
                <div class="hanging-string"></div>
                <div class="hanging-nail"></div>
                <img id="modalImage" src="" alt="Artwork">
            </div>'''

info_css_patch_old = '''        .modal-info {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }'''
info_css_patch_new = '''        .modal-info {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            background: rgba(0,0,0,0.8); /* Card on the wall */
            padding: 30px;
            border-radius: 10px;
            color: #fff;
        }'''

# Home patches
home_img_old = '''                <div class="card-img-wrapper">
                    {% if artwork.image %}'''
home_img_new = '''                <div class="card-img-wrapper" onclick="openModal('{{ artwork.title|escapejs }}', '{{ artwork.seller.username|escapejs }}', '', '{{ artwork.price }}', '{% if artwork.image %}{{ artwork.image.url }}{% else %}{% static \\'images/art1.png\\' %}{% endif %}', '{{ artwork.id }}', '{{ artwork.status }}', false)" style="cursor:pointer;">
                    {% if artwork.image %}'''

home_replacements = [
    ('<!-- CALL TO ACTION -->', testimonial_html),
    (old_css, new_css),
    (old_frame_css, new_frame_css),
    (hook_html_old, hook_html_new),
    (info_css_patch_old, info_css_patch_new),
    (home_img_old, home_img_new)
]

patch_file(home_path, home_replacements)

# Buyer patches
buyer_img_old = '''                    <a href="{% url 'gallery:artwork_detail' artwork.id %}" class="card-link">
                    {% if artwork.image %}'''
buyer_img_new = '''                    <a href="javascript:void(0);" onclick="openModal('{{ artwork.title|escapejs }}', '{{ artwork.seller.username|escapejs }}', '{{ artwork.seller.profile.bio|escapejs|default:\\'\\' }}', '{{ artwork.price }}', '{% if artwork.image %}{{ artwork.image.url }}{% else %}https://picsum.photos/800/600?random={{ forloop.counter }}{% endif %}', '{{ artwork.id }}', '{{ artwork.status }}', true)" class="card-link">
                    {% if artwork.image %}'''

buyer_img_old_b = '''                    <a href="{% url 'gallery:artwork_detail' artwork.id %}" class="card-link">
                            <div class="card-title">{{ artwork.title }}</div>
                            <div class="card-subtitle">{{ artwork.category.name }} | by {{ artwork.seller.username }}</div>
                        </a>'''
buyer_img_new_b = '''                    <a href="javascript:void(0);" onclick="openModal('{{ artwork.title|escapejs }}', '{{ artwork.seller.username|escapejs }}', '{{ artwork.seller.profile.bio|escapejs|default:\\'\\' }}', '{{ artwork.price }}', '{% if artwork.image %}{{ artwork.image.url }}{% else %}https://picsum.photos/800/600?random={{ forloop.counter }}{% endif %}', '{{ artwork.id }}', '{{ artwork.status }}', true)" class="card-link">
                            <div class="card-title">{{ artwork.title }}</div>
                            <div class="card-subtitle">{{ artwork.category.name }} | by {{ artwork.seller.username }}</div>
                        </a>'''

buyer_replacements = [
    (old_css, new_css),
    (old_frame_css, new_frame_css),
    (hook_html_old, hook_html_new),
    (info_css_patch_old, info_css_patch_new),
    (buyer_img_old, buyer_img_new),
    (buyer_img_old_b, buyer_img_new_b)
]

patch_file(buyer_path, buyer_replacements)
