"""Image processing and OCR capabilities."""
import pytesseract
import easyocr
from PIL import Image
import cv2
import numpy as np
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Process images and extract text using OCR."""
    
    def __init__(self):
        try:
            self.easyocr_reader = easyocr.Reader(['en', 'ar'])  # English and Arabic
        except Exception as e:
            logger.warning(f"EasyOCR initialization failed: {e}")
            self.easyocr_reader = None
    
    def extract_text_ocr(self, image_path: str, use_easyocr: bool = True) -> str:
        """Extract text from image using OCR."""
        try:
            if use_easyocr and self.easyocr_reader:
                return self._extract_with_easyocr(image_path)
            else:
                return self._extract_with_tesseract(image_path)
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return ""
    
    def _extract_with_easyocr(self, image_path: str) -> str:
        """Extract text using EasyOCR."""
        try:
            results = self.easyocr_reader.readtext(image_path)
            text = " ".join([result[1] for result in results])
            return text
        except Exception as e:
            logger.error(f"EasyOCR extraction failed: {e}")
            return ""
    
    def _extract_with_tesseract(self, image_path: str) -> str:
        """Extract text using Tesseract OCR."""
        try:
            image = Image.open(image_path)
            # Preprocess image for better OCR
            image = self._preprocess_image(image)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            logger.error(f"Tesseract extraction failed: {e}")
            return ""
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image to improve OCR accuracy."""
        try:
            # Convert to OpenCV format
            img_array = np.array(image)
            
            # Convert to grayscale
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Apply thresholding
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Convert back to PIL Image
            return Image.fromarray(thresh)
        except Exception as e:
            logger.warning(f"Image preprocessing failed: {e}")
            return image

