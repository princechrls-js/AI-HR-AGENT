import pytesseract
from PIL import Image, ImageFilter, ImageEnhance
import fitz  # PyMuPDF
import io
from app.core.logging import logger

class OCRService:
    def __init__(self):
        # Tesseract path might need to be configured for Windows
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pass

    def extract_text_from_image(self, image_bytes: bytes) -> str:
        """Enhanced OCR with image preprocessing for better accuracy."""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to grayscale
            image = image.convert('L')
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            
            # Sharpen
            image = image.filter(ImageFilter.SHARPEN)
            
            # Scale up small images for better OCR
            width, height = image.size
            if width < 1000:
                scale = 2
                image = image.resize((width * scale, height * scale), Image.LANCZOS)
            
            # Use Tesseract with optimized config
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(image, config=custom_config)
            return text
        except Exception as e:
            logger.error(f"OCR image extraction failed: {e}")
            return ""

    def extract_text_from_scanned_pdf(self, pdf_path: str) -> str:
        """Extract text from scanned PDF with high-DPI rendering for accuracy."""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                # Render at 300 DPI for much better OCR accuracy
                mat = fitz.Matrix(300/72, 300/72)
                pix = page.get_pixmap(matrix=mat)
                img_bytes = pix.tobytes("png")
                text += self.extract_text_from_image(img_bytes) + "\n\n"
            doc.close()
            return text
        except Exception as e:
            logger.error(f"OCR PDF extraction failed: {e}")
            return ""

ocr_service = OCRService()
