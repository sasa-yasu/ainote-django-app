import os
import django
from dotenv import load_dotenv

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AinoteProject.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
username = os.getenv("ADMIN_USER")
email = os.getenv("ADMIN_EMAIL")
password = os.getenv("ADMIN_PWD")

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print("Superuser created successfully!")
else:
    print("Superuser already exists.")
