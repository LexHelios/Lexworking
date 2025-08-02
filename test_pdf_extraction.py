#!/usr/bin/env python3
"""
Test PDF extraction to see what's being extracted
"""
import PyPDF2
import sys

def test_pdf_extraction(pdf_path):
    """Test what PyPDF2 extracts from the PDF"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)
            
            print(f"PDF has {num_pages} pages")
            print("="*60)
            
            # Extract first 3 pages
            for i in range(min(3, num_pages)):
                page = pdf_reader.pages[i]
                text = page.extract_text()
                
                print(f"\nPage {i+1}:")
                print("-"*40)
                print(f"Text length: {len(text)} characters")
                print(f"First 500 chars:\n{text[:500]}")
                print(f"\nContains 'Maple Leaf': {'Maple Leaf' in text}")
                print(f"Contains '759 Burr Oak': {'759 Burr Oak' in text}")
                print(f"Contains numbers: {any(char.isdigit() for char in text)}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_pdf_extraction(sys.argv[1])
    else:
        print("Usage: python test_pdf_extraction.py <pdf_path>")
        print("\nTesting with CIBA PDF if it exists...")
        # Try common paths
        import os
        for path in ["CIBA Res Supplemental.pdf", "../CIBA Res Supplemental.pdf", "../../CIBA Res Supplemental.pdf"]:
            if os.path.exists(path):
                print(f"\nFound PDF at: {path}")
                test_pdf_extraction(path)
                break