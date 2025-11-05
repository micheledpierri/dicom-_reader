"""
Image Processing Filters
Various filters for DICOM image enhancement and processing
"""

import numpy as np
from scipy import ndimage
from skimage import filters, exposure, morphology
import cv2
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class ImageFilters:
    """Collection of image processing filters"""

    @staticmethod
    def adjust_brightness(image: np.ndarray, value: float) -> np.ndarray:
        """
        Adjust image brightness

        Args:
            image: Input image array
            value: Brightness adjustment value (-100 to 100)

        Returns:
            Brightness-adjusted image
        """
        adjusted = image.astype(np.float32) + value
        return np.clip(adjusted, 0, 255).astype(np.uint8)

    @staticmethod
    def adjust_contrast(image: np.ndarray, factor: float) -> np.ndarray:
        """
        Adjust image contrast

        Args:
            image: Input image array
            factor: Contrast factor (0.5 to 3.0, 1.0 is no change)

        Returns:
            Contrast-adjusted image
        """
        mean = image.mean()
        adjusted = (image - mean) * factor + mean
        return np.clip(adjusted, 0, 255).astype(np.uint8)

    @staticmethod
    def sharpen(image: np.ndarray, amount: float = 1.0) -> np.ndarray:
        """
        Sharpen image using unsharp masking

        Args:
            image: Input image array
            amount: Sharpening amount (0 to 2.0)

        Returns:
            Sharpened image
        """
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(image, (0, 0), 3)

        # Sharpen using weighted addition
        sharpened = cv2.addWeighted(image, 1.0 + amount, blurred, -amount, 0)

        return np.clip(sharpened, 0, 255).astype(np.uint8)

    @staticmethod
    def gaussian_blur(image: np.ndarray, sigma: float = 1.0) -> np.ndarray:
        """
        Apply Gaussian blur

        Args:
            image: Input image array
            sigma: Standard deviation for Gaussian kernel

        Returns:
            Blurred image
        """
        return ndimage.gaussian_filter(image, sigma=sigma).astype(np.uint8)

    @staticmethod
    def median_filter(image: np.ndarray, size: int = 3) -> np.ndarray:
        """
        Apply median filter for noise reduction

        Args:
            image: Input image array
            size: Size of the median filter kernel

        Returns:
            Filtered image
        """
        return ndimage.median_filter(image, size=size).astype(np.uint8)

    @staticmethod
    def edge_detection_sobel(image: np.ndarray) -> np.ndarray:
        """
        Detect edges using Sobel operator

        Args:
            image: Input image array

        Returns:
            Edge-detected image
        """
        edges = filters.sobel(image)
        edges = (edges * 255).astype(np.uint8)
        return edges

    @staticmethod
    def edge_detection_canny(image: np.ndarray,
                            low_threshold: float = 50,
                            high_threshold: float = 150) -> np.ndarray:
        """
        Detect edges using Canny edge detector

        Args:
            image: Input image array
            low_threshold: Lower threshold for edge detection
            high_threshold: Upper threshold for edge detection

        Returns:
            Edge-detected image
        """
        edges = cv2.Canny(image, low_threshold, high_threshold)
        return edges

    @staticmethod
    def histogram_equalization(image: np.ndarray) -> np.ndarray:
        """
        Apply histogram equalization for contrast enhancement

        Args:
            image: Input image array

        Returns:
            Equalized image
        """
        return cv2.equalizeHist(image)

    @staticmethod
    def adaptive_histogram_equalization(image: np.ndarray,
                                       clip_limit: float = 2.0,
                                       tile_grid_size: Tuple[int, int] = (8, 8)) -> np.ndarray:
        """
        Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)

        Args:
            image: Input image array
            clip_limit: Threshold for contrast limiting
            tile_grid_size: Size of grid for histogram equalization

        Returns:
            Equalized image
        """
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        return clahe.apply(image)

    @staticmethod
    def gamma_correction(image: np.ndarray, gamma: float = 1.0) -> np.ndarray:
        """
        Apply gamma correction

        Args:
            image: Input image array
            gamma: Gamma value (< 1.0 brightens, > 1.0 darkens)

        Returns:
            Gamma-corrected image
        """
        # Normalize to 0-1
        normalized = image.astype(np.float32) / 255.0

        # Apply gamma correction
        corrected = np.power(normalized, gamma)

        # Scale back to 0-255
        return (corrected * 255).astype(np.uint8)

    @staticmethod
    def invert(image: np.ndarray) -> np.ndarray:
        """
        Invert image colors

        Args:
            image: Input image array

        Returns:
            Inverted image
        """
        return 255 - image

    @staticmethod
    def threshold_binary(image: np.ndarray, threshold: int = 127) -> np.ndarray:
        """
        Apply binary thresholding

        Args:
            image: Input image array
            threshold: Threshold value (0-255)

        Returns:
            Thresholded binary image
        """
        _, binary = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY)
        return binary

    @staticmethod
    def threshold_otsu(image: np.ndarray) -> np.ndarray:
        """
        Apply Otsu's automatic thresholding

        Args:
            image: Input image array

        Returns:
            Thresholded binary image
        """
        threshold_value = filters.threshold_otsu(image)
        binary = image > threshold_value
        return (binary * 255).astype(np.uint8)

    @staticmethod
    def morphology_erode(image: np.ndarray, kernel_size: int = 3) -> np.ndarray:
        """
        Apply morphological erosion

        Args:
            image: Input image array
            kernel_size: Size of the structuring element

        Returns:
            Eroded image
        """
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        return cv2.erode(image, kernel, iterations=1)

    @staticmethod
    def morphology_dilate(image: np.ndarray, kernel_size: int = 3) -> np.ndarray:
        """
        Apply morphological dilation

        Args:
            image: Input image array
            kernel_size: Size of the structuring element

        Returns:
            Dilated image
        """
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        return cv2.dilate(image, kernel, iterations=1)

    @staticmethod
    def morphology_open(image: np.ndarray, kernel_size: int = 3) -> np.ndarray:
        """
        Apply morphological opening (erosion followed by dilation)

        Args:
            image: Input image array
            kernel_size: Size of the structuring element

        Returns:
            Opened image
        """
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

    @staticmethod
    def morphology_close(image: np.ndarray, kernel_size: int = 3) -> np.ndarray:
        """
        Apply morphological closing (dilation followed by erosion)

        Args:
            image: Input image array
            kernel_size: Size of the structuring element

        Returns:
            Closed image
        """
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        return cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)

    @staticmethod
    def denoise_bilateral(image: np.ndarray,
                         d: int = 9,
                         sigma_color: float = 75,
                         sigma_space: float = 75) -> np.ndarray:
        """
        Apply bilateral filter for edge-preserving noise reduction

        Args:
            image: Input image array
            d: Diameter of each pixel neighborhood
            sigma_color: Filter sigma in the color space
            sigma_space: Filter sigma in the coordinate space

        Returns:
            Denoised image
        """
        return cv2.bilateralFilter(image, d, sigma_color, sigma_space)

    @staticmethod
    def denoise_non_local_means(image: np.ndarray,
                               h: float = 10,
                               template_window_size: int = 7,
                               search_window_size: int = 21) -> np.ndarray:
        """
        Apply non-local means denoising

        Args:
            image: Input image array
            h: Filter strength
            template_window_size: Size of template patch
            search_window_size: Size of search area

        Returns:
            Denoised image
        """
        return cv2.fastNlMeansDenoising(
            image,
            None,
            h,
            template_window_size,
            search_window_size
        )


class FilterPresets:
    """Predefined filter presets for common medical imaging tasks"""

    @staticmethod
    def enhance_bone(image: np.ndarray) -> np.ndarray:
        """Enhance bone visibility"""
        # Sharpen and adjust contrast
        sharpened = ImageFilters.sharpen(image, amount=1.5)
        enhanced = ImageFilters.adjust_contrast(sharpened, factor=1.3)
        return enhanced

    @staticmethod
    def enhance_soft_tissue(image: np.ndarray) -> np.ndarray:
        """Enhance soft tissue visibility"""
        # Apply CLAHE for local contrast enhancement
        enhanced = ImageFilters.adaptive_histogram_equalization(image, clip_limit=3.0)
        return enhanced

    @staticmethod
    def reduce_noise(image: np.ndarray) -> np.ndarray:
        """Reduce image noise while preserving edges"""
        # Apply bilateral filter
        denoised = ImageFilters.denoise_bilateral(image, d=9, sigma_color=75, sigma_space=75)
        return denoised

    @staticmethod
    def enhance_edges(image: np.ndarray) -> np.ndarray:
        """Enhance image edges"""
        # Sharpen and apply edge enhancement
        sharpened = ImageFilters.sharpen(image, amount=2.0)
        return sharpened
