import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # File upload settings
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 50 * 1024 * 1024))
    UPLOAD_FOLDER = 'uploads'
    OUTPUT_FOLDER = 'output'
    
    # Allowed file extensions
    ALLOWED_IMAGES = {'png', 'jpg', 'jpeg', 'bmp', 'gif', 'tiff', 'webp'}
    ALLOWED_PDFS = {'pdf'}
    
    # CORS settings - Update with your actual domain
    CORS_ORIGINS = [
        'http://localhost:5500',
        'http://localhost:8000',
        'http://127.0.0.1:5500',
        'http://127.0.0.1:8000',
        # Add your InfinityFree domain when deployed
        'https://your-domain.infinityfreeapp.com',
        'https://yourdomain.com'
    ]

class DevelopmentConfig(Config):
    DEBUG = True
    ENV = 'development'

class ProductionConfig(Config):
    DEBUG = False
    ENV = 'production'

# Select configuration based on environment
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}