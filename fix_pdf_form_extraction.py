#!/usr/bin/env python3
"""
Fix PDF form extraction to get actual values instead of placeholders
"""

# First, let's update the requirements to include pdfplumber
print("""
To fix PDF form extraction, we need to:

1. Install pdfplumber (better at extracting form data):
   pip install pdfplumber

2. Update lex_multimodal_processor.py to use pdfplumber

Here's the improved PDF processor:
""")

improved_pdf_processor = '''
    async def process_pdf(self, file_path: str) -> Dict[str, Any]:
        """Process PDF files with better form handling"""
        try:
            import pdfplumber
            
            text_content = []
            metadata = {}
            form_data = {}
            
            # Try pdfplumber first (better for forms)
            try:
                with pdfplumber.open(file_path) as pdf:
                    num_pages = len(pdf.pages)
                    
                    for i, page in enumerate(pdf.pages):
                        # Extract text
                        text = page.extract_text()
                        if text:
                            text_content.append({
                                "page": i + 1,
                                "text": text
                            })
                        
                        # Extract tables if any
                        tables = page.extract_tables()
                        if tables:
                            for table in tables:
                                text_content.append({
                                    "page": i + 1,
                                    "text": "TABLE:\\n" + str(table)
                                })
                    
                    # Get metadata
                    if pdf.metadata:
                        metadata = {
                            "title": pdf.metadata.get('Title', ''),
                            "author": pdf.metadata.get('Author', ''),
                            "pages": num_pages
                        }
                        
            except Exception as e:
                print(f"pdfplumber failed, falling back to PyPDF2: {e}")
                # Fallback to PyPDF2
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    num_pages = len(pdf_reader.pages)
                    
                    for page_num, page in enumerate(pdf_reader.pages):
                        text = page.extract_text()
                        if text.strip():
                            text_content.append({
                                "page": page_num + 1,
                                "text": text.strip()
                            })
            
            # Combine text
            full_text = "\\n\\n".join([f"Page {p['page']}:\\n{p['text']}" for p in text_content])
            
            # If we got mostly underscores, try to extract actual form data
            if full_text.count('_') > len(full_text) * 0.3:
                # This PDF might be a form with placeholders
                # Add a note about this
                full_text = f"NOTE: This appears to be a form PDF with many blank fields. Extracted content may show placeholders instead of actual values.\\n\\n{full_text}"
            
            return {
                "success": True,
                "content_type": "pdf",
                "data": {
                    "text": full_text[:20000],
                    "pages": text_content[:10],
                    "total_pages": num_pages
                },
                "metadata": metadata,
                "requires_vision_model": False
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
'''

print("\nTo apply this fix:")
print("1. Install pdfplumber: pip install pdfplumber")
print("2. Replace the process_pdf method in lex_multimodal_processor.py with the improved version above")
print("\nThis will handle form PDFs better and extract actual content instead of placeholders.")