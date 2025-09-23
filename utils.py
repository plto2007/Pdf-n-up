import io
from typing import Optional
import fitz  # PyMuPDF

def validate_pdf_file(uploaded_file) -> bool:
    """
    Validate if the uploaded file is a valid PDF
    """
    try:
        # Reset file pointer to beginning
        uploaded_file.seek(0)
        
        # Read file content
        file_content = uploaded_file.read()
        
        # Reset file pointer again for later use
        uploaded_file.seek(0)
        
        # Check if it's a valid PDF by trying to open it
        doc = fitz.open(stream=file_content, filetype="pdf")
        doc.close()
        
        return True
        
    except Exception as e:
        print(f"PDF validation error: {str(e)}")
        return False

def get_pdf_info(pdf_content: bytes) -> Optional[dict]:
    """
    Extract basic information from PDF content
    """
    try:
        doc = fitz.open(stream=pdf_content, filetype="pdf")
        
        metadata = doc.metadata or {}
        info = {
            'page_count': len(doc),
            'title': metadata.get('title', ''),
            'author': metadata.get('author', ''),
            'creator': metadata.get('creator', ''),
            'producer': metadata.get('producer', ''),
            'creation_date': metadata.get('creationDate', ''),
            'modification_date': metadata.get('modDate', '')
        }
        
        doc.close()
        return info
        
    except Exception as e:
        print(f"Error getting PDF info: {str(e)}")
        return None

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"

def create_error_message(error_type: str, details: str = "") -> str:
    """
    Create standardized error messages
    """
    error_messages = {
        'invalid_pdf': '❌ Invalid PDF file. Please upload a valid PDF document.',
        'processing_error': '❌ Error processing PDF. Please try again.',
        'upload_error': '❌ Error uploading file. Please check the file and try again.',
        'memory_error': '❌ File too large. Please try with a smaller file.',
        'general_error': '❌ An unexpected error occurred.'
    }
    
    base_message = error_messages.get(error_type, error_messages['general_error'])
    
    if details:
        return f"{base_message}\nDetails: {details}"
    
    return base_message
