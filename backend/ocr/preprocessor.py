"""
Image preprocessing for better OCR accuracy.
Applies denoising, binarization, deskewing, and contrast enhancement.
"""

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import logging
from typing import Union
import io

try:
    import cv2
    _CV2_AVAILABLE = True
except ImportError:
    cv2 = None
    _CV2_AVAILABLE = False

logger = logging.getLogger(__name__)


class ImagePreprocessor:
    """Preprocess images for optimal OCR accuracy."""

    @staticmethod
    def preprocess(image_input: Union[str, bytes, np.ndarray]) -> np.ndarray:
        """
        Full preprocessing pipeline for OCR.
        Steps: load → resize → grayscale → denoise → binarize → deskew
        """
        # Load image
        img = ImagePreprocessor._load_image(image_input)

        # Step 1: Resize to optimal DPI (300 DPI equivalent)
        img = ImagePreprocessor._resize_for_ocr(img)

        # Step 2: Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Step 3: Remove noise
        denoised = ImagePreprocessor._denoise(gray)

        # Step 4: Enhance contrast
        contrasted = ImagePreprocessor._enhance_contrast(denoised)

        # Step 5: Binarize (convert to black/white)
        binary = ImagePreprocessor._binarize(contrasted)

        # Step 6: Deskew (correct rotation)
        deskewed = ImagePreprocessor._deskew(binary)

        # Step 7: Remove borders
        cleaned = ImagePreprocessor._remove_borders(deskewed)

        logger.info("Image preprocessing complete")
        return cleaned

    @staticmethod
    def preprocess_pan_card(image_input: Union[str, bytes, np.ndarray]) -> np.ndarray:
        """
        Specialized preprocessing for PAN cards.
        PAN cards have specific layout — optimize accordingly.
        """
        img = ImagePreprocessor._load_image(image_input)
        img = ImagePreprocessor._resize_for_ocr(img, target_width=1200)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # PAN cards often have colored backgrounds — use adaptive threshold
        denoised = cv2.fastNlMeansDenoising(gray, h=10)
        binary = cv2.adaptiveThreshold(
            denoised, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        deskewed = ImagePreprocessor._deskew(binary)
        return deskewed

    @staticmethod
    def preprocess_salary_slip(image_input: Union[str, bytes, np.ndarray]) -> np.ndarray:
        """
        Specialized preprocessing for salary slips.
        Salary slips are typically printed documents — optimize for text.
        """
        img = ImagePreprocessor._load_image(image_input)
        img = ImagePreprocessor._resize_for_ocr(img, target_width=1600)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Salary slips often have tables and fine print
        denoised = cv2.bilateralFilter(gray, 9, 75, 75)
        _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        deskewed = ImagePreprocessor._deskew(binary)
        return deskewed

    @staticmethod
    def _load_image(image_input: Union[str, bytes, np.ndarray]) -> np.ndarray:
        """Load image from file path, bytes, or numpy array."""
        if isinstance(image_input, np.ndarray):
            return image_input
        elif isinstance(image_input, bytes):
            nparr = np.frombuffer(image_input, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError("Failed to decode image from bytes")
            return img
        elif isinstance(image_input, str):
            img = cv2.imread(image_input)
            if img is None:
                raise FileNotFoundError(f"Image not found: {image_input}")
            return img
        else:
            raise TypeError(f"Unsupported image type: {type(image_input)}")

    @staticmethod
    def _resize_for_ocr(img: np.ndarray, target_width: int = 1000) -> np.ndarray:
        """Resize image for optimal OCR (minimum 300 DPI equivalent)."""
        h, w = img.shape[:2]
        if w < target_width:
            scale = target_width / w
            new_w = int(w * scale)
            new_h = int(h * scale)
            img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
        return img

    @staticmethod
    def _denoise(gray: np.ndarray) -> np.ndarray:
        """Remove noise using Non-Local Means Denoising."""
        return cv2.fastNlMeansDenoising(gray, None, h=10, templateWindowSize=7, searchWindowSize=21)

    @staticmethod
    def _enhance_contrast(gray: np.ndarray) -> np.ndarray:
        """Enhance contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)."""
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(gray)

    @staticmethod
    def _binarize(gray: np.ndarray) -> np.ndarray:
        """Convert to binary (black/white) using Otsu's thresholding."""
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return binary

    @staticmethod
    def _deskew(binary: np.ndarray) -> np.ndarray:
        """Correct image skew/rotation."""
        try:
            coords = np.column_stack(np.where(binary > 0))
            if len(coords) < 5:
                return binary
            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle
            if abs(angle) < 0.5:
                return binary
            h, w = binary.shape
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(binary, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            return rotated
        except Exception as e:
            logger.warning(f"Deskew failed: {e}")
            return binary

    @staticmethod
    def _remove_borders(binary: np.ndarray) -> np.ndarray:
        """Remove black borders from the image."""
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            x, y, w, h = cv2.boundingRect(max(contours, key=cv2.contourArea))
            margin = 5
            x = max(0, x - margin)
            y = max(0, y - margin)
            w = min(binary.shape[1] - x, w + 2 * margin)
            h = min(binary.shape[0] - y, h + 2 * margin)
            return binary[y:y+h, x:x+w]
        return binary