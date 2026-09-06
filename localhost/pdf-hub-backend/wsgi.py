# wsgi.py
import sys
import os

# Add the project directory to Python path
# Update YOUR_USERNAME with your PythonAnywhere username
path = '/home/YOUR_USERNAME/pdf-hub-backend'
if path not in sys.path:
    sys.path.append(path)

# Import the Flask app
from app import app as application

# PythonAnywhere looks for 'application'
# This is the entry point for the WSGI server