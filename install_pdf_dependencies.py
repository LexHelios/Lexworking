#!/usr/bin/env python3
"""
🔱 Install Enhanced PDF Processing Dependencies 🔱
JAI MAHAKAAL! Quick setup for PDF/OCR support
"""
import os
import sys
import subprocess
import platform

def install_dependencies():
    """Install all required dependencies for enhanced PDF processing"""
    
    print("🔱 Installing Enhanced PDF Processing Dependencies...")
    print("=" * 60)
    
    # Python packages to install
    packages = [
        "pytesseract==0.3.10",
        "pymupdf==1.23.8", 
        "pdf2image==1.16.3",
        "python-doctr[torch]==0.6.0",
        "python-pptx==0.6.23",
        "torch",
        "torchvision",
        "transformers",
        "opencv-python"
    ]
    
    # Install Python packages
    print("\n📦 Installing Python packages...")
    for package in packages:
        print(f"  Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"  ✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Failed to install {package}: {e}")
    
    # Platform-specific instructions
    print("\n🖥️ Platform-specific requirements:")
    print("=" * 60)
    
    system = platform.system()
    
    if system == "Linux":
        print("\n🐧 Linux detected. Install Tesseract OCR:")
        print("  sudo apt update")
        print("  sudo apt install tesseract-ocr")
        print("  sudo apt install libtesseract-dev")
        print("  sudo apt install tesseract-ocr-eng")  # English language pack
        print("\n  For additional languages:")
        print("  sudo apt install tesseract-ocr-[lang]")
        
    elif system == "Windows":
        print("\n🪟 Windows detected. Install Tesseract OCR:")
        print("  1. Download installer from: https://github.com/UB-Mannheim/tesseract/wiki")
        print("  2. Run the installer")
        print("  3. Add Tesseract to PATH or set TESSDATA_PREFIX environment variable")
        print("\n  Alternative (using Chocolatey):")
        print("  choco install tesseract")
        
    elif system == "Darwin":  # macOS
        print("\n🍎 macOS detected. Install Tesseract OCR:")
        print("  brew install tesseract")
        print("  brew install tesseract-lang  # For additional languages")
    
    # GPU support check
    print("\n🎮 GPU Support:")
    print("=" * 60)
    
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✅ CUDA is available! GPU: {torch.cuda.get_device_name(0)}")
            print(f"   CUDA version: {torch.version.cuda}")
            print("   Doctr will use GPU acceleration for OCR")
        else:
            print("⚠️  No CUDA GPU detected. OCR will run on CPU")
            print("   For GPU support, install CUDA toolkit and GPU drivers")
    except ImportError:
        print("❌ PyTorch not installed properly")
    
    # Test imports
    print("\n🧪 Testing imports...")
    print("=" * 60)
    
    test_imports = [
        ("pytesseract", "Tesseract OCR Python wrapper"),
        ("fitz", "PyMuPDF for PDF processing"),
        ("pdf2image", "PDF to image conversion"),
        ("doctr", "Document Text Recognition (GPU OCR)"),
        ("cv2", "OpenCV for image processing"),
        ("pptx", "PowerPoint processing")
    ]
    
    all_good = True
    for module, description in test_imports:
        try:
            __import__(module)
            print(f"✅ {module} ({description}) - OK")
        except ImportError as e:
            print(f"❌ {module} ({description}) - FAILED: {e}")
            all_good = False
    
    # Final status
    print("\n" + "=" * 60)
    if all_good:
        print("✅ All dependencies installed successfully!")
        print("\n🚀 You can now use enhanced PDF processing with:")
        print("   - OCR for scanned documents")
        print("   - GPU acceleration (if available)")
        print("   - Support for PDF, images, Word, Excel, PowerPoint")
    else:
        print("⚠️  Some dependencies failed to install")
        print("   Please check the errors above and install manually")
    
    # Usage example
    print("\n📖 Usage example:")
    print("=" * 60)
    print("""
from enhanced_pdf_processor import enhanced_pdf_processor

# Process a PDF with OCR
result = await enhanced_pdf_processor.process_file(
    "document.pdf",
    extract_images=True,
    extract_tables=True,
    ocr_mode="auto"  # auto, always, never
)

print(f"Text extracted: {len(result['text'])} characters")
print(f"OCR used: {result['metadata']['ocr_performed']}")
""")

if __name__ == "__main__":
    install_dependencies()