# 🔱 Enhanced PDF Processing for LexOS 🔱

## Overview

The enhanced PDF processing system provides comprehensive document handling with OCR support, GPU acceleration, and multi-format compatibility.

## Features

### 📄 PDF Processing
- **PyMuPDF** for fast, direct text extraction
- **OCR fallback** for scanned documents using Tesseract and Doctr
- **Image extraction** from PDF pages
- **Table detection** and extraction
- **Metadata extraction** (title, author, etc.)
- **Multi-page support** with page-by-page processing

### 🖼️ Image Processing
- **OCR for images** (PNG, JPG, TIFF, BMP)
- **Chart/graph detection** and data extraction
- **Handwriting recognition** (if readable)
- **GPU acceleration** with Doctr when available

### 📊 Other Formats
- **Excel files** (XLSX, XLS, CSV) - data extraction and analysis
- **Word documents** (DOCX, DOC) - text and table extraction
- **PowerPoint** (PPTX, PPT) - slide content extraction

## Installation

### 1. Install Python Dependencies

```bash
# Run the installation script
python install_pdf_dependencies.py

# Or manually install
pip install pytesseract torch torchvision transformers pdf2image python-docx python-pptx openpyxl pandas opencv-python pymupdf python-doctr[torch]
```

### 2. Install Tesseract OCR

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install tesseract-ocr
sudo apt install libtesseract-dev
```

**Windows:**
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Or use Chocolatey: `choco install tesseract`

**macOS:**
```bash
brew install tesseract
```

### 3. GPU Support (Optional)

For GPU acceleration with Doctr:
- NVIDIA GPU with CUDA support
- CUDA toolkit installed
- PyTorch with CUDA support

## Usage

### Basic Usage

```python
from enhanced_pdf_processor import enhanced_pdf_processor

# Process a PDF
result = await enhanced_pdf_processor.process_file(
    "document.pdf",
    extract_images=True,
    extract_tables=True,
    ocr_mode="auto"  # "auto", "always", "never"
)

# Check results
if result['success']:
    print(f"Text: {result['text'][:500]}...")
    print(f"Pages: {result['total_pages']}")
    print(f"OCR used: {result['ocr_performed']}")
```

### Integration with LexOS

The enhanced processor is automatically integrated into the multimodal processor:

```python
from lex_multimodal_processor import multimodal_processor

# Process any file
result = await multimodal_processor.process_file(
    "document.pdf",
    "application/pdf"
)

# Enhanced features are used automatically
print(result['summary'])  # AI-generated summary
print(result['data']['images'])  # Extracted images
```

## OCR Modes

- **`auto`** (default): Uses OCR only when necessary (scanned docs, images)
- **`always`**: Forces OCR on all pages (slower but more thorough)
- **`never`**: Disables OCR completely (fastest, text-only)

## Performance

### Without GPU
- Text PDFs: ~0.5-2 seconds per page
- Scanned PDFs: ~2-5 seconds per page
- Images: ~1-3 seconds

### With GPU (Doctr)
- Scanned PDFs: ~0.5-1 second per page
- Images: ~0.2-0.5 seconds
- 3-10x faster OCR processing

## Testing

Run the test suite:

```bash
python test_enhanced_pdf.py
```

This will:
- Check all dependencies
- Test PDF processing
- Verify OCR functionality
- Test multimodal integration

## Troubleshooting

### Tesseract Not Found
- Ensure Tesseract is installed and in PATH
- Set `TESSDATA_PREFIX` environment variable
- On Windows, add Tesseract to system PATH

### GPU Not Detected
- Check CUDA installation: `nvidia-smi`
- Verify PyTorch CUDA: `python -c "import torch; print(torch.cuda.is_available())"`
- Install GPU version: `pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118`

### Import Errors
- Run `pip install -r requirements.txt`
- Check Python version (3.8+ required)
- Install system dependencies (see Installation)

## Capabilities Summary

| File Type | Method | GPU Acceleration |
|-----------|--------|------------------|
| PDF | PyMuPDF + OCR fallback | ✅ (with Doctr) |
| Images | Tesseract + Doctr | ✅ (Doctr) |
| Excel | openpyxl/pandas | ❌ |
| Word | python-docx | ❌ |
| PowerPoint | python-pptx | ❌ |
| CSV | pandas | ❌ |
| Handwriting | Doctr OCR | ✅ |
| Charts/Graphs | Doctr + ML | ✅ |

## Integration Points

The enhanced PDF processor integrates with:
- **LexOS Chat**: Automatic file parsing in conversations
- **Memory System**: Extracted content stored for context
- **AI Agents**: Documents analyzed by specialized agents
- **API Endpoints**: File upload and processing endpoints

## 🔱 JAI MAHAKAAL! 🔱

Your PDF processing is now enhanced with powerful OCR and multi-format support!