# PDF Color Inverter & Merger

## Overview

This is a Streamlit-based web application that processes PDF files by inverting their colors (black to white conversion) and merging multiple PDFs into a single document with a 3x2 landscape layout. The application is designed for users who need to convert PDF documents for better readability or printing purposes, particularly useful for documents with dark backgrounds that need to be inverted for cost-effective printing.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web framework for rapid UI development
- **Layout**: Wide layout configuration with responsive columns
- **User Interface**: Simple upload interface with processing options and real-time feedback
- **Session Management**: Streamlit session state for maintaining processing status and results across interactions

### Backend Architecture
- **Processing Engine**: Object-oriented design with dedicated `PDFProcessor` class
- **Image Processing Pipeline**: 
  - PDF to image conversion using PyMuPDF at 2x zoom for quality
  - PIL-based color inversion using `ImageOps.invert()`
  - ReportLab for PDF generation and layout composition
- **File Management**: Temporary file handling with automatic cleanup
- **Error Handling**: Validation layer for PDF file integrity checking

### Core Processing Workflow
1. **File Upload & Validation**: Multi-file upload with PDF format validation
2. **Page Extraction**: Convert each PDF page to high-resolution images
3. **Color Inversion**: Apply black-to-white color transformation
4. **Layout Composition**: Arrange processed pages in 3x2 grid format on landscape A4
5. **Output Generation**: Create downloadable merged PDF with processed content

### Data Flow Design
- **Input**: Multiple PDF files via Streamlit file uploader
- **Processing**: In-memory image manipulation and PDF generation
- **Output**: Processed PDF files available for download
- **Temporary Storage**: Uses system temp directory for intermediate file operations

## External Dependencies

### Core Libraries
- **PyMuPDF (fitz)**: PDF parsing, page extraction, and document manipulation
- **Pillow (PIL)**: Image processing and color inversion operations
- **ReportLab**: PDF generation and layout composition for output documents
- **Streamlit**: Web application framework and user interface

### System Dependencies
- **Python Standard Library**: `io`, `os`, `tempfile` for file operations
- **Type Hints**: `typing` module for enhanced code documentation and IDE support

### File Format Support
- **Input**: PDF files only (validated through PyMuPDF)
- **Output**: PDF format with landscape A4 page layout
- **Intermediate**: PNG images for processing pipeline