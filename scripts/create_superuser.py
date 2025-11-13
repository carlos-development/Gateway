import os
import sys
from pathlib import Path
import django

# Asegurar que el root del proyecto esté en sys.path para poder importar `config`
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

username = 'Admin'
email = 'admin@admin.com'
password = 'sistemas,.'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f'Superusuario creado: {username} / {email}')
else:
    print(f'Usuario {username} ya existe')
