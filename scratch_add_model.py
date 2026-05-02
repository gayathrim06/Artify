import os
import sys

path = r'c:\Users\91894\OneDrive\Desktop\AWT\art_gallery\gallery\models.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

model_code = '''
class Testimonial(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='testimonials')
    role_at_time = models.CharField(max_length=20, default='buyer')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=5)
    comment = models.TextField()
    admin_reply = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Testimonial by {self.user.username}"
'''
if 'class Testimonial' not in content:
    content = content + '\n' + model_code

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
