"""
DICOM Parser
Extracts and processes metadata from DICOM files
"""

import pydicom
import numpy as np
from typing import Dict, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DICOMParser:
    """Parses DICOM files and extracts relevant information"""

    @staticmethod
    def get_patient_info(dataset: pydicom.Dataset) -> Dict:
        """
        Extract patient information from DICOM dataset

        Args:
            dataset: pydicom.Dataset object

        Returns:
            Dictionary containing patient information
        """
        return {
            'patient_name': str(dataset.get('PatientName', 'Unknown')),
            'patient_id': str(dataset.get('PatientID', 'Unknown')),
            'patient_sex': str(dataset.get('PatientSex', 'Unknown')),
            'patient_birth_date': str(dataset.get('PatientBirthDate', 'Unknown')),
            'patient_age': str(dataset.get('PatientAge', 'Unknown'))
        }

    @staticmethod
    def get_study_info(dataset: pydicom.Dataset) -> Dict:
        """
        Extract study information from DICOM dataset

        Args:
            dataset: pydicom.Dataset object

        Returns:
            Dictionary containing study information
        """
        return {
            'study_instance_uid': str(dataset.get('StudyInstanceUID', '')),
            'study_date': str(dataset.get('StudyDate', 'Unknown')),
            'study_time': str(dataset.get('StudyTime', 'Unknown')),
            'study_description': str(dataset.get('StudyDescription', 'Unknown')),
            'accession_number': str(dataset.get('AccessionNumber', 'Unknown'))
        }

    @staticmethod
    def get_series_info(dataset: pydicom.Dataset) -> Dict:
        """
        Extract series information from DICOM dataset

        Args:
            dataset: pydicom.Dataset object

        Returns:
            Dictionary containing series information
        """
        return {
            'series_instance_uid': str(dataset.get('SeriesInstanceUID', '')),
            'series_number': int(dataset.get('SeriesNumber', 0)),
            'series_description': str(dataset.get('SeriesDescription', 'Unknown')),
            'modality': str(dataset.get('Modality', 'Unknown')),
            'series_date': str(dataset.get('SeriesDate', 'Unknown')),
            'series_time': str(dataset.get('SeriesTime', 'Unknown'))
        }

    @staticmethod
    def get_instance_info(dataset: pydicom.Dataset) -> Dict:
        """
        Extract instance information from DICOM dataset

        Args:
            dataset: pydicom.Dataset object

        Returns:
            Dictionary containing instance information
        """
        return {
            'sop_instance_uid': str(dataset.get('SOPInstanceUID', '')),
            'instance_number': int(dataset.get('InstanceNumber', 0)),
            'acquisition_number': int(dataset.get('AcquisitionNumber', 0)),
            'image_position': dataset.get('ImagePositionPatient', None),
            'image_orientation': dataset.get('ImageOrientationPatient', None)
        }

    @staticmethod
    def get_image_info(dataset: pydicom.Dataset) -> Dict:
        """
        Extract image-specific information

        Args:
            dataset: pydicom.Dataset object

        Returns:
            Dictionary containing image information
        """
        return {
            'rows': int(dataset.get('Rows', 0)),
            'columns': int(dataset.get('Columns', 0)),
            'pixel_spacing': dataset.get('PixelSpacing', None),
            'slice_thickness': float(dataset.get('SliceThickness', 0)) if 'SliceThickness' in dataset else None,
            'slice_location': float(dataset.get('SliceLocation', 0)) if 'SliceLocation' in dataset else None,
            'bits_allocated': int(dataset.get('BitsAllocated', 0)),
            'bits_stored': int(dataset.get('BitsStored', 0)),
            'window_center': dataset.get('WindowCenter', None),
            'window_width': dataset.get('WindowWidth', None),
            'rescale_intercept': float(dataset.get('RescaleIntercept', 0)),
            'rescale_slope': float(dataset.get('RescaleSlope', 1))
        }

    @staticmethod
    def get_pixel_array(dataset: pydicom.Dataset) -> Optional[np.ndarray]:
        """
        Extract pixel data as numpy array

        Args:
            dataset: pydicom.Dataset object

        Returns:
            Numpy array containing pixel data or None if extraction fails
        """
        try:
            pixel_array = dataset.pixel_array

            # Apply rescale slope and intercept
            if 'RescaleSlope' in dataset and 'RescaleIntercept' in dataset:
                pixel_array = pixel_array * dataset.RescaleSlope + dataset.RescaleIntercept

            return pixel_array
        except Exception as e:
            logger.error(f"Error extracting pixel array: {str(e)}")
            return None

    @staticmethod
    def get_window_level_image(dataset: pydicom.Dataset,
                               window_center: Optional[float] = None,
                               window_width: Optional[float] = None) -> Optional[np.ndarray]:
        """
        Apply window/level to image for display

        Args:
            dataset: pydicom.Dataset object
            window_center: Window center value (uses default from DICOM if None)
            window_width: Window width value (uses default from DICOM if None)

        Returns:
            Numpy array with windowed pixel values (0-255)
        """
        pixel_array = DICOMParser.get_pixel_array(dataset)

        if pixel_array is None:
            return None

        # Get window values from DICOM if not provided
        if window_center is None:
            wc = dataset.get('WindowCenter', None)
            if wc is not None:
                window_center = float(wc[0]) if isinstance(wc, (list, tuple)) else float(wc)
            else:
                window_center = (pixel_array.max() + pixel_array.min()) / 2

        if window_width is None:
            ww = dataset.get('WindowWidth', None)
            if ww is not None:
                window_width = float(ww[0]) if isinstance(ww, (list, tuple)) else float(ww)
            else:
                window_width = pixel_array.max() - pixel_array.min()

        # Apply window/level
        img_min = window_center - window_width / 2
        img_max = window_center + window_width / 2

        windowed = np.clip(pixel_array, img_min, img_max)
        windowed = ((windowed - img_min) / (img_max - img_min) * 255).astype(np.uint8)

        return windowed

    @staticmethod
    def get_all_metadata(dataset: pydicom.Dataset) -> Dict:
        """
        Extract all metadata from DICOM dataset

        Args:
            dataset: pydicom.Dataset object

        Returns:
            Dictionary containing all metadata
        """
        return {
            'patient': DICOMParser.get_patient_info(dataset),
            'study': DICOMParser.get_study_info(dataset),
            'series': DICOMParser.get_series_info(dataset),
            'instance': DICOMParser.get_instance_info(dataset),
            'image': DICOMParser.get_image_info(dataset)
        }
