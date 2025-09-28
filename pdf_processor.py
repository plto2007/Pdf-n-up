import io
import os
from typing import List, Optional
from PIL import Image, ImageOps
import pymupdf as fitz  # PyMuPDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.utils import ImageReader
import tempfile

Zoom = 4.0

class PDFProcessor:
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
    
    def process_pdfs(self, pdf_paths: List[str], invert_colors: bool = True, 
                    merge_files: bool = True, layout_3x2: bool = True) -> List[bytes]:
        """
        Main processing function that handles the complete workflow
        """
        try:
            # Step 1: Process each PDF individually
            processed_pdfs = []
            all_pages = []
            
            for pdf_path in pdf_paths:
                # Open PDF and extract pages
                doc = fitz.open(pdf_path)
                
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    
                    # Convert page to image
                    global Zoom
                    mat = fitz.Matrix(Zoom, Zoom)  # 2x zoom for better quality
                    pix = page.get_pixmap(matrix=mat)
                    img_data = pix.tobytes("png")
                    
                    # Process image (invert colors if requested)
                    image = Image.open(io.BytesIO(img_data))
                    if invert_colors:
                        image = self.invert_image_colors(image)
                    
                    all_pages.append(image)
                
                doc.close()
            
            # Step 2: Create output PDFs
            if layout_3x2:
                # Group pages into sets of 6 for 3x2 layout
                page_groups = [all_pages[i:i+6] for i in range(0, len(all_pages), 6)]
                
                if merge_files:
                    # Single PDF with all page groups
                    pdf_data = self.create_3x2_landscape_pdf(page_groups)
                    return [pdf_data] if pdf_data else []
                else:
                    # Separate PDF for each original file
                    result_pdfs = []
                    pages_per_file = [len(fitz.open(path)) for path in pdf_paths]
                    start_idx = 0
                    
                    for file_pages in pages_per_file:
                        file_page_groups = []
                        end_idx = start_idx + file_pages
                        file_pages_list = all_pages[start_idx:end_idx]
                        
                        # Group this file's pages into 3x2 layouts
                        for i in range(0, len(file_pages_list), 6):
                            file_page_groups.append(file_pages_list[i:i+6])
                        
                        pdf_data = self.create_3x2_landscape_pdf(file_page_groups)
                        if pdf_data:
                            result_pdfs.append(pdf_data)
                        
                        start_idx = end_idx
                    
                    return result_pdfs
            else:
                # Original layout - just process colors
                if merge_files:
                    # Single merged PDF
                    pdf_data = self.create_original_layout_pdf(all_pages)
                    return [pdf_data] if pdf_data else []
                else:
                    # Separate PDFs
                    result_pdfs = []
                    pages_per_file = [len(fitz.open(path)) for path in pdf_paths]
                    start_idx = 0
                    
                    for file_pages in pages_per_file:
                        end_idx = start_idx + file_pages
                        file_pages_list = all_pages[start_idx:end_idx]
                        pdf_data = self.create_original_layout_pdf(file_pages_list)
                        if pdf_data:
                            result_pdfs.append(pdf_data)
                        start_idx = end_idx
                    
                    return result_pdfs
            
        except Exception as e:
            print(f"Error processing PDFs: {str(e)}")
            return []
    
    def invert_image_colors(self, image: Image.Image) -> Image.Image:
        """
        Invert the colors of an image (black becomes white, white becomes black)
        """
        try:
            # Convert to RGB if not already
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Invert colors
            inverted_image = ImageOps.invert(image)
            return inverted_image
            
        except Exception as e:
            print(f"Error inverting image colors: {str(e)}")
            return image
    
    def create_3x2_landscape_pdf(self, page_groups: List[List[Image.Image]]) -> Optional[bytes]:
        """
        Create a PDF with 3x2 page layout in landscape orientation
        """
        try:
            buffer = io.BytesIO()
            
            # Use landscape A4 size
            page_width, page_height = landscape(A4)
            c = canvas.Canvas(buffer, pagesize=landscape(A4))
            
            # Calculate dimensions for 3x2 grid
            cols, rows = 2, 3
            cell_width = page_width / cols
            cell_height = page_height / rows
            
            # Add margin
            margin = 10
            img_width = cell_width - 2 * margin
            img_height = cell_height - 2 * margin
            
            for group in page_groups:
                # Start a new page for each group of 6
                for i, page_image in enumerate(group):
                    if i >= 6:  # Maximum 6 images per page
                        break
                    
                    # Calculate position in grid
                    col = i % cols
                    row = i // cols
                    
                    x = col * cell_width + margin
                    y = page_height - (row + 1) * cell_height + margin
                    
                    # Resize image to fit cell while maintaining aspect ratio
                    page_image_resized = self.resize_image_to_fit(
                        page_image, img_width, img_height
                    )
                    
                    # Save image to temporary buffer
                    img_buffer = io.BytesIO()
                    page_image_resized.save(img_buffer, format='PNG')
                    img_buffer.seek(0)
                    
                    # Add image to PDF
                    c.drawImage(ImageReader(img_buffer), x, y, 
                              width=page_image_resized.width, 
                              height=page_image_resized.height)
                
                c.showPage()  # New page for next group
            
            c.save()
            return buffer.getvalue()
            
        except Exception as e:
            print(f"Error creating 3x2 landscape PDF: {str(e)}")
            return None
    
    def create_original_layout_pdf(self, pages: List[Image.Image]) -> Optional[bytes]:
        """
        Create a PDF with original page layout (one image per page)
        """
        try:
            buffer = io.BytesIO()
            page_width, page_height = A4
            c = canvas.Canvas(buffer, pagesize=A4)
            
            margin = 20
            max_width = page_width - 2 * margin
            max_height = page_height - 2 * margin
            
            for page_image in pages:
                # Resize image to fit page
                resized_image = self.resize_image_to_fit(page_image, max_width, max_height)
                
                # Center image on page
                x = (page_width - resized_image.width) / 2
                y = (page_height - resized_image.height) / 2
                
                # Save image to temporary buffer
                img_buffer = io.BytesIO()
                resized_image.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                
                # Add image to PDF
                c.drawImage(ImageReader(img_buffer), x, y, 
                          width=resized_image.width, 
                          height=resized_image.height)
                
                c.showPage()
            
            c.save()
            return buffer.getvalue()
            
        except Exception as e:
            print(f"Error creating original layout PDF: {str(e)}")
            return None
    
    def resize_image_to_fit(self, image: Image.Image, max_width: float, max_height: float) -> Image.Image:
        """
        Resize image to fit within specified dimensions while maintaining aspect ratio
        """
        try:
            # Calculate scaling factor
            width_ratio = max_width / image.width
            height_ratio = max_height / image.height
            scale_factor = min(width_ratio, height_ratio)
            
            # Calculate new dimensions
            new_width = int(image.width * scale_factor)
            new_height = int(image.height * scale_factor)
            
            # Resize image
            resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            return resized_image
            
        except Exception as e:
            print(f"Error resizing image: {str(e)}")
            return image
