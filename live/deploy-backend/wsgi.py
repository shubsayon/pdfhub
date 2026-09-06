# wsgi.py - FOR PYTHONANYWHERE DEPLOYMENT
import sys
import os

path = '/home/shubhamsayon/pdf-hub-backend'
if path not in sys.path:
    sys.path.append(path)

from app import app as application