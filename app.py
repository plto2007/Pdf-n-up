import streamlit as st
import tempfile
import os
from io import BytesIO
import zipfile
from pdf_processor import PDFProcessor
from utils import validate_pdf_file

def main():
    st.set_page_config(
        page_title="PDF Color Inverter & Merger",
        page_icon="📄",
        layout="wide"
    )
    
    st.title("📄 PDF Color Inverter & Merger")
    st.markdown("Upload PDF files to invert colors and merge them into a 3x2 landscape layout")
    
    # Initialize session state
    if 'processed_pdfs' not in st.session_state:
        st.session_state.processed_pdfs = []
    if 'processing_complete' not in st.session_state:
        st.session_state.processing_complete = False
    
    # File upload section
    st.header("📤 Upload PDF Files")
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=['pdf'],
        accept_multiple_files=True,
        help="Upload one or more PDF files to process"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} PDF file(s) uploaded successfully")
        
        # Display uploaded files info
        with st.expander("📋 Uploaded Files Details"):
            for i, file in enumerate(uploaded_files):
                st.write(f"**{i+1}. {file.name}** - {file.size} bytes")
        
        # Processing options
        st.header("⚙️ Processing Options")
        
        col1, col2 = st.columns(2)
        with col1:
            invert_colors = st.checkbox("🔄 Invert Colors (Black ↔ White)", value=True)
        with col2:
            merge_files = st.checkbox("📑 Merge All Files", value=True)
        
        layout_option = st.selectbox(
            "📐 Page Layout",
            ["3x2 Landscape Grid", "Original Layout"],
            index=0
        )
        
        # Process button
        if st.button("🚀 Process PDFs", type="primary"):
            if not uploaded_files:
                st.error("❌ Please upload at least one PDF file")
                return
            
            with st.spinner("🔄 Processing PDFs... This may take a few moments"):
                try:
                    processor = PDFProcessor()
                    
                    # Save uploaded files temporarily
                    temp_files = []
                    for uploaded_file in uploaded_files:
                        if validate_pdf_file(uploaded_file):
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                                tmp_file.write(uploaded_file.read())
                                temp_files.append(tmp_file.name)
                        else:
                            st.error(f"❌ Invalid PDF file: {uploaded_file.name}")
                            return
                    
                    # Process PDFs
                    result = processor.process_pdfs(
                        temp_files,
                        invert_colors=invert_colors,
                        merge_files=merge_files,
                        layout_3x2=layout_option == "3x2 Landscape Grid"
                    )
                    
                    if result:
                        st.session_state.processed_pdfs = result
                        st.session_state.processing_complete = True
                        st.success("✅ PDFs processed successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to process PDFs. Please try again.")
                    
                    # Cleanup temporary files
                    for temp_file in temp_files:
                        try:
                            os.unlink(temp_file)
                        except:
                            pass
                            
                except Exception as e:
                    st.error(f"❌ Error processing PDFs: {str(e)}")
    
    # Display results if processing is complete
    if st.session_state.processing_complete and st.session_state.processed_pdfs:
        st.header("📊 Processing Results")
        
        for i, pdf_data in enumerate(st.session_state.processed_pdfs):
            with st.expander(f"📄 Processed PDF {i+1}", expanded=True):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**File size:** {len(pdf_data)} bytes")
                    st.write(f"**Processing:** Color inverted, 3x2 landscape layout")
                
                with col2:
                    st.download_button(
                        label=f"⬇️ Download PDF {i+1}",
                        data=pdf_data,
                        file_name=f"processed_pdf_{i+1}.pdf",
                        mime="application/pdf"
                    )
        
        # Download all as ZIP
        if len(st.session_state.processed_pdfs) > 1:
            st.subheader("📦 Download All Files")
            
            # Create ZIP file
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for i, pdf_data in enumerate(st.session_state.processed_pdfs):
                    zip_file.writestr(f"processed_pdf_{i+1}.pdf", pdf_data)
            
            st.download_button(
                label="⬇️ Download All PDFs (ZIP)",
                data=zip_buffer.getvalue(),
                file_name="processed_pdfs.zip",
                mime="application/zip"
            )
        
        # Reset button
        if st.button("🔄 Process New Files"):
            st.session_state.processed_pdfs = []
            st.session_state.processing_complete = False
            st.rerun()
    
    # Instructions
    with st.sidebar:
        st.header("📖 How to Use")
        st.markdown("""
        1. **Upload PDF Files**: Click 'Choose PDF files' or drag & drop your PDF files
        2. **Configure Options**: Choose whether to invert colors and merge files
        3. **Select Layout**: Choose 3x2 landscape grid or keep original layout
        4. **Process**: Click 'Process PDFs' to start the conversion
        5. **Download**: Download individual files or all files as a ZIP
        
        ### ✨ Features
        - 🔄 **Color Inversion**: Converts black text/graphics to white on black background
        - 📑 **File Merging**: Combines multiple PDFs into one
        - 📐 **3x2 Grid Layout**: Arranges 6 pages per sheet in landscape orientation
        - 📤 **Batch Processing**: Handle multiple files at once
        - ⬇️ **Easy Download**: Get processed files individually or as a ZIP
        """)
        
        st.header("⚠️ Important Notes")
        st.markdown("""
        - Maximum file size depends on your system memory
        - Color inversion works best with text-based PDFs
        - Processing time varies with file size and complexity
        - Large files may take several minutes to process
        """)

if __name__ == "__main__":
    main()
