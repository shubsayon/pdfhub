import os
import uuid
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import configuration and PDF processor
from config import Config
from pdf_hub import PDFHub

# Initialize Flask app
app = Flask(__name__)

# Load configuration
app.config.from_object(Config)

# Enable CORS
CORS(app, origins=app.config['CORS_ORIGINS'])

# Initialize PDF processor
hub = PDFHub(
    upload_dir=app.config['UPLOAD_FOLDER'],
    output_dir=app.config['OUTPUT_FOLDER']
)

# ===== Helper Functions =====

def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """
    Check if file has an allowed extension
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_uploaded_files(files, allowed_extensions):
    """
    Save uploaded files to temporary storage
    """
    saved_paths = []
    
    for file in files:
        if not file or file.filename == '':
            return None, 'Empty file uploaded'
        
        if not allowed_file(file.filename, allowed_extensions):
            return None, f'Invalid file type: {file.filename}'
        
        try:
            original_name = secure_filename(file.filename)
            unique_id = str(uuid.uuid4())[:8]
            safe_filename = f'{unique_id}_{original_name}'
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
            
            file.save(filepath)
            saved_paths.append(filepath)
            
        except Exception as e:
            for path in saved_paths:
                try:
                    os.remove(path)
                except:
                    pass
            return None, f'Error saving file: {str(e)}'
    
    return saved_paths, None

# ===== Root & Static Routes =====

@app.route('/')
def index():
    """Root endpoint - welcome message"""
    return jsonify({
        'message': 'Welcome to PDFHub API',
        'version': '2.0.0',
        'author': 'Shubham Sayon',
        'endpoints': {
            'health': '/api/health',
            'info': '/api/info',
            'convert': '/api/convert (POST - multipart/form-data)',
            'merge': '/api/merge (POST - multipart/form-data)'
        },
        'documentation': 'Visit /api/info for detailed information',
        'github': 'https://github.com/yourusername/pdf-hub-backend'
    })

@app.route('/favicon.ico')
def favicon():
    """Return empty response for favicon"""
    return '', 204

# ===== API Endpoints =====

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'service': 'PDFHub API',
        'version': '2.0.0'
    })

@app.route('/api/info', methods=['GET'])
def service_info():
    """Service information endpoint"""
    return jsonify({
        'name': 'PDFHub',
        'version': '2.0.0',
        'author': 'Shubham Sayon',
        'description': 'Convert images to PDF and merge PDFs',
        'features': [
            'Convert images (JPG, PNG, BMP, GIF, TIFF, WEBP) to PDF',
            'Merge multiple PDFs',
            'Custom filename support',
            'Drag and drop interface',
            'Progress tracking'
        ],
        'endpoints': {
            'GET /': 'Welcome message',
            'GET /api/health': 'Health check',
            'GET /api/info': 'Service information',
            'POST /api/convert': 'Convert images to PDF',
            'POST /api/merge': 'Merge PDFs'
        },
        'max_file_size': '50MB',
        'supported_formats': {
            'images': ['JPG', 'JPEG', 'PNG', 'BMP', 'GIF', 'TIFF', 'WEBP'],
            'pdfs': ['PDF']
        }
    })

@app.route('/api/convert', methods=['POST'])
def convert_images():
    """
    Convert images to PDF
    
    Request: multipart/form-data with 'files' field(s)
    Optional: 'filename' field for custom PDF name
    
    Returns: PDF file download or error JSON
    """
    try:
        # Check if files were uploaded
        if 'files' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No files uploaded'
            }), 400
        
        files = request.files.getlist('files')
        if not files or files[0].filename == '':
            return jsonify({
                'success': False,
                'error': 'No files selected'
            }), 400
        
        # Save uploaded files
        saved_paths, error = save_uploaded_files(files, app.config['ALLOWED_IMAGES'])
        if error:
            return jsonify({
                'success': False,
                'error': error
            }), 400
        
        # Get custom filename
        custom_name = request.form.get('filename', None)
        
        # Convert to PDF
        result = hub.images_to_pdf(saved_paths, custom_name)
        
        # Clean up uploaded files
        hub.cleanup(saved_paths)
        
        if not result['success']:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
        
        # Return the generated PDF
        return send_file(
            result['file_path'],
            as_attachment=True,
            download_name=result['file_name'],
            mimetype='application/pdf'
        )
        
    except Exception as e:
        # Clean up any remaining files
        try:
            hub.cleanup_all()
        except:
            pass
        
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/api/merge', methods=['POST'])
def merge_pdfs():
    """
    Merge PDFs
    
    Request: multipart/form-data with 'files' field(s)
    Optional: 'filename' field for custom PDF name
    
    Returns: PDF file download or error JSON
    """
    try:
        # Check if files were uploaded
        if 'files' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No files uploaded'
            }), 400
        
        files = request.files.getlist('files')
        if not files or files[0].filename == '':
            return jsonify({
                'success': False,
                'error': 'No files selected'
            }), 400
        
        # Save uploaded files
        saved_paths, error = save_uploaded_files(files, app.config['ALLOWED_PDFS'])
        if error:
            return jsonify({
                'success': False,
                'error': error
            }), 400
        
        # Get custom filename
        custom_name = request.form.get('filename', None)
        
        # Merge PDFs
        result = hub.merge_pdfs(saved_paths, custom_name)
        
        # Clean up uploaded files
        hub.cleanup(saved_paths)
        
        if not result['success']:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
        
        # Return the merged PDF
        return send_file(
            result['file_path'],
            as_attachment=True,
            download_name=result['file_name'],
            mimetype='application/pdf'
        )
        
    except Exception as e:
        # Clean up any remaining files
        try:
            hub.cleanup_all()
        except:
            pass
        
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

# ===== Error Handlers =====

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({
        'success': False,
        'error': f'File too large. Maximum size: {app.config["MAX_CONTENT_LENGTH"] // (1024*1024)}MB'
    }), 413

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(405)
def method_not_allowed(e):
    """Handle method not allowed errors"""
    return jsonify({
        'success': False,
        'error': 'Method not allowed'
    }), 405

@app.errorhandler(500)
def server_error(e):
    """Handle server errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

# ===== Main Entry Point =====
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=app.config['DEBUG']
    )