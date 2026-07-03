# modules/text_extractor.py

import PyPDF2
import docx
import pytesseract
from PIL import Image
import os
import re

# -------------------------
# Set Tesseract OCR path (Custom path for Windows)
# -------------------------
# Update this path to match your Tesseract installation, or set the env var TESSERACT_CMD.
TESSERACT_CMD = os.getenv("TESSERACT_CMD", r"C:\Program Files\tesseract-main\tesseract.exe")
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

# -------------------------
# Optional: OCR for scanned PDFs
# -------------------------
# If you install Poppler on Windows, you can also set POPPLER_PATH as an env var
# (e.g. C:\poppler-xx\Library\bin) so pdf2image can locate the binaries.
POPPLER_PATH = os.getenv("POPPLER_PATH")

try:
    import pdf2image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# -------------------------
# Text cleaning function
# -------------------------
def clean_text(text):
    """
    Remove extra spaces, newlines, and special characters
    """
    text = re.sub(r'\r\n|\r', '\n', text)     # Normalize newlines
    text = re.sub(r'\n+', '\n', text)         # Multiple newlines → single
    text = re.sub(r'\s+', ' ', text)          # Multiple spaces → single
    text = text.strip()
    return text

# -------------------------
# Main text extraction function
# -------------------------
def extract_text(file_path):
    """
    Extract text from PDF or DOCX file
    Supports:
    - PDF (text-based)
    - PDF (scanned via OCR if pdf2image + pytesseract available)
    - DOCX
    """
    text = ""

    file_ext = os.path.splitext(file_path)[1].lower()

    # -------------------------
    # PDF Extraction
    # -------------------------
    if file_ext == ".pdf":
        try:
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"[Warning] PDF text extraction failed: {e}")

        # -------------------------
        # OCR for scanned PDFs
        # -------------------------
        if OCR_AVAILABLE and text.strip() == "":
            try:
                convert_kwargs = {}
                if POPPLER_PATH:
                    convert_kwargs["poppler_path"] = POPPLER_PATH

                images = pdf2image.convert_from_path(file_path, **convert_kwargs)
                for img in images:
                    text += pytesseract.image_to_string(img) + "\n"
            except Exception as e:
                print(
                    "[Warning] OCR failed (pdf2image/poppler). "
                    "Install Poppler and/or set POPPLER_PATH. "
                    f"Error: {e}"
                )

    # -------------------------
    # DOCX Extraction
    # -------------------------
    elif file_ext == ".docx":
        try:
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        except Exception as e:
            print(f"[Warning] DOCX extraction failed: {e}")

    else:
        raise ValueError("Unsupported file format. Only PDF and DOCX allowed.")

    # -------------------------
    # Clean up extracted text
    # -------------------------
    text = clean_text(text)

    return text