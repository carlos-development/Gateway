"""
==========================================
PASSENGER WSGI - CONFIGURACIÓN CPANEL
==========================================
Este archivo es el punto de entrada para Passenger (usado por cPanel)
"""

import os
import sys

# Añadir el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(__file__))

# Configurar Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Importar la aplicación WSGI de Django
from config.wsgi import application
