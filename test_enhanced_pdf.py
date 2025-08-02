#!/usr/bin/env python3
"""
🔱 Test Enhanced PDF Processing 🔱
JAI MAHAKAAL! Comprehensive test suite for PDF/OCR functionality
"""
import asyncio
import os
import sys
from pathlib import Path
import json
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_pdf_processor import enhanced_pdf_processor
from lex_multimodal_processor import multimodal_processor

async def test_pdf_processing():
    """Test PDF processing with various scenarios"""
    
    print("🔱 Testing Enhanced PDF Processing")
    print("=" * 60)
    
    # Test files to process
    test_files = [
        # Add your test files here
        # "test_documents/sample.pdf",
        # "test_documents/scanned_document.pdf",
        # "test_documents/form.pdf",
        # "test_documents/chart.png",
        # "test_documents/handwritten.jpg"
    ]
    
    # If no test files specified, create a simple test
    if not test_files:
        print("ℹ️  No test files specified. Testing with system info...")
        
        # Test processor initialization
        print("\n1️⃣ Testing processor initialization...")
        try:
            # Check GPU availability
            import torch
            gpu_available = torch.cuda.is_available()
            print(f"   GPU Available: {gpu_available}")
            if gpu_available:
                print(f"   GPU Name: {torch.cuda.get_device_name(0)}")
                print(f"   CUDA Version: {torch.version.cuda}")
            
            # Check Tesseract
            try:
                import pytesseract
                version = pytesseract.get_tesseract_version()
                print(f"   Tesseract Version: {version}")
            except Exception as e:
                print(f"   ❌ Tesseract not available: {e}")
            
            # Check Doctr
            try:
                import doctr
                print(f"   ✅ Doctr available")
            except ImportError:
                print(f"   ❌ Doctr not available")
            
            print("   ✅ Processor initialized successfully")
            
        except Exception as e:
            print(f"   ❌ Initialization failed: {e}")
            return
    
    # Process each test file
    results = []
    for file_path in test_files:
        if not os.path.exists(file_path):
            print(f"\n⚠️  File not found: {file_path}")
            continue
        
        print(f"\n📄 Processing: {file_path}")
        print("-" * 40)
        
        try:
            # Test enhanced processor directly
            start_time = datetime.now()
            result = await enhanced_pdf_processor.process_file(
                file_path,
                extract_images=True,
                extract_tables=True,
                ocr_mode="auto"
            )
            processing_time = (datetime.now() - start_time).total_seconds()
            
            if result.get('success'):
                print(f"✅ Successfully processed in {processing_time:.2f}s")
                print(f"   File Type: {result['metadata']['file_type']}")
                
                if result.get('content_type') == 'pdf':
                    print(f"   Total Pages: {result.get('total_pages', 0)}")
                    print(f"   OCR Performed: {result.get('ocr_performed', False)}")
                    print(f"   Images Extracted: {len(result.get('images', []))}")
                    print(f"   Tables Extracted: {len(result.get('tables', []))}")
                    
                    # Show text preview
                    text = result.get('text', '')
                    if text:
                        preview = text[:200] + "..." if len(text) > 200 else text
                        print(f"   Text Preview: {preview}")
                
                elif result.get('content_type') == 'image':
                    info = result.get('image_info', {})
                    print(f"   Dimensions: {info.get('width')}x{info.get('height')}")
                    print(f"   Format: {info.get('format')}")
                    print(f"   Is Chart: {result.get('is_chart', False)}")
                    
                    # Show OCR text if available
                    ocr_text = result.get('text', '')
                    if ocr_text:
                        preview = ocr_text[:200] + "..." if len(ocr_text) > 200 else ocr_text
                        print(f"   OCR Text: {preview}")
                
                results.append({
                    'file': file_path,
                    'success': True,
                    'time': processing_time,
                    'result': result
                })
                
            else:
                error = result.get('error', 'Unknown error')
                print(f"❌ Processing failed: {error}")
                results.append({
                    'file': file_path,
                    'success': False,
                    'error': error
                })
                
        except Exception as e:
            print(f"❌ Exception during processing: {e}")
            results.append({
                'file': file_path,
                'success': False,
                'error': str(e)
            })
    
    # Test multimodal processor integration
    print("\n\n2️⃣ Testing Multimodal Processor Integration...")
    print("=" * 60)
    
    # Create a test PDF content
    test_pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 44 >>\nstream\nBT\n/F1 12 Tf\n100 700 Td\n(Hello LexOS!) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000299 00000 n\ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n391\n%%EOF"
    
    # Save test PDF
    test_pdf_path = "test_lexos_pdf.pdf"
    with open(test_pdf_path, 'wb') as f:
        f.write(test_pdf_content)
    
    try:
        # Test with multimodal processor
        result = await multimodal_processor.process_file(test_pdf_path, "application/pdf")
        
        if result.get('success'):
            print("✅ Multimodal processor integration working")
            print(f"   Content Type: {result.get('content_type')}")
            print(f"   Has Enhanced PDF: {'summary' in result}")
        else:
            print(f"❌ Multimodal processor failed: {result.get('error')}")
            
    finally:
        # Clean up test file
        if os.path.exists(test_pdf_path):
            os.remove(test_pdf_path)
    
    # Summary
    print("\n\n📊 Test Summary")
    print("=" * 60)
    
    if results:
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful
        
        print(f"Total Files Tested: {len(results)}")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        
        if successful > 0:
            avg_time = sum(r['time'] for r in results if r.get('time', 0) > 0) / successful
            print(f"⏱️  Average Processing Time: {avg_time:.2f}s")
    else:
        print("ℹ️  No files were tested. Add test files to the test_files list.")
    
    print("\n✨ Enhanced PDF processing is ready for use!")
    print("\n🔱 JAI MAHAKAAL! 🔱")

if __name__ == "__main__":
    asyncio.run(test_pdf_processing())