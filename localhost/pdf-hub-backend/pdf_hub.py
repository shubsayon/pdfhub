import os
import shutil
from datetime import datetime
from typing import List, Optional, Dict, Any
from PIL import Image
from PyPDF2 import PdfMerger, PdfReader

class PDFHub:
    """
    Core PDF processing engine
    Converts images to PDF and merges PDF files
    """
    
    def __init__(self, upload_dir: str = 'uploads', output_dir: str = 'output'):
        """
        Initialize the PDF processor
        
        Args:
            upload_dir: Directory for temporary uploads
            output_dir: Directory for generated PDFs
        """
        self.upload_dir = upload_dir
        self.output_dir = output_dir
        
        # Create directories if they don't exist
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
    
    def images_to_pdf(self, image_paths: List[str], output_filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Convert multiple images to a single PDF
        
        Args:
            image_paths: List of image file paths
            output_filename: Custom name for output PDF (optional)
            
        Returns:
            Dict with success status, file info, or error message
        """
        try:
            if not image_paths:
                return {
                    'success': False,
                    'error': 'No images provided'
                }
            
            # Validate and process images
            images = []
            for img_path in image_paths:
                if not os.path.exists(img_path):
                    return {
                        'success': False,
                        'error': f'File not found: {os.path.basename(img_path)}'
                    }
                
                try:
                    img = Image.open(img_path)
                    # Convert to RGB if necessary (for PDF compatibility)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    images.append(img)
                except Exception as e:
                    return {
                        'success': False,
                        'error': f'Failed to process image {os.path.basename(img_path)}: {str(e)}'
                    }
            
            # Generate output filename if not provided
            if not output_filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_filename = f'PDFHub_{timestamp}.pdf'
            
            # Ensure .pdf extension
            if not output_filename.lower().endswith('.pdf'):
                output_filename += '.pdf'
            
            output_path = os.path.join(self.output_dir, output_filename)
            
            # Save images as PDF
            if len(images) == 1:
                images[0].save(output_path, 'PDF', resolution=100.0)
            else:
                images[0].save(
                    output_path,
                    'PDF',
                    resolution=100.0,
                    save_all=True,
                    append_images=images[1:]
                )
            
            # Get file size
            file_size = os.path.getsize(output_path)
            
            return {
                'success': True,
                'file_path': output_path,
                'file_name': output_filename,
                'file_size': file_size,
                'page_count': len(images),
                'message': f'Successfully converted {len(images)} image(s) to PDF'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'PDF creation failed: {str(e)}'
            }
    
    def merge_pdfs(self, pdf_paths: List[str], output_filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Merge multiple PDFs into one
        
        Args:
            pdf_paths: List of PDF file paths
            output_filename: Custom name for merged PDF (optional)
            
        Returns:
            Dict with success status, file info, or error message
        """
        try:
            if not pdf_paths:
                return {
                    'success': False,
                    'error': 'No PDFs provided'
                }
            
            merger = PdfMerger()
            total_pages = 0
            
            for pdf_path in pdf_paths:
                if not os.path.exists(pdf_path):
                    return {
                        'success': False,
                        'error': f'File not found: {os.path.basename(pdf_path)}'
                    }
                
                try:
                    with open(pdf_path, 'rb') as f:
                        reader = PdfReader(f)
                        total_pages += len(reader.pages)
                        merger.append(reader)
                except Exception as e:
                    return {
                        'success': False,
                        'error': f'Failed to process PDF {os.path.basename(pdf_path)}: {str(e)}'
                    }
            
            # Generate output filename if not provided
            if not output_filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_filename = f'Merged_PDF_{timestamp}.pdf'
            
            # Ensure .pdf extension
            if not output_filename.lower().endswith('.pdf'):
                output_filename += '.pdf'
            
            output_path = os.path.join(self.output_dir, output_filename)
            
            # Write merged PDF
            merger.write(output_path)
            merger.close()
            
            # Get file size
            file_size = os.path.getsize(output_path)
            
            return {
                'success': True,
                'file_path': output_path,
                'file_name': output_filename,
                'file_size': file_size,
                'page_count': total_pages,
                'message': f'Successfully merged {len(pdf_paths)} PDF(s)'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'PDF merge failed: {str(e)}'
            }
    
    def cleanup(self, file_paths: List[str]) -> None:
        """
        Clean up temporary files
        
        Args:
            file_paths: List of file paths to delete
        """
        for path in file_paths:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception:
                pass  # Silently ignore cleanup errors
    
    def cleanup_all(self) -> None:
        """
        Clean up entire upload and output directories
        Use with caution - deletes all temporary files
        """
        try:
            shutil.rmtree(self.upload_dir)
            shutil.rmtree(self.output_dir)
            os.makedirs(self.upload_dir, exist_ok=True)
            os.makedirs(self.output_dir, exist_ok=True)
        except Exception:
            pass  # Silently ignore cleanup errors