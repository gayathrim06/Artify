import os

path = r'c:\Users\91894\OneDrive\Desktop\AWT\art_gallery\templates\users\buyer_dashboard.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("default:'\"\"'", 'default:""')
content = content.replace("default:\\'\\'\\'", 'default:""')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
