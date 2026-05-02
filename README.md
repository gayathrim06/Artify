# Art Gallery Django Project

## MySQL Backend Setup

1. Install the MySQL driver for Python:

```bash
pip install PyMySQL
```

2. Create the database in MySQL Workbench:

```sql
CREATE DATABASE art_gallery
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER 'artuser'@'localhost' IDENTIFIED BY 'yourpassword';
GRANT ALL PRIVILEGES ON art_gallery.* TO 'artuser'@'localhost';
FLUSH PRIVILEGES;
```

3. Update `art_gallery/art_gallery/settings.py` with your MySQL credentials:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'art_gallery',
        'USER': 'artuser',
        'PASSWORD': 'yourpassword',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
```

4. Run Django migrations:

```bash
cd c:\Users\91894\OneDrive\Desktop\AWT\art_gallery
py manage.py makemigrations
py manage.py migrate
```

5. Create a superuser:

```bash
py manage.py createsuperuser
```

6. Start the server:

```bash
py manage.py runserver
```
