"""
DICOM File Loader
Handles loading and validation of DICOM files from various sources
"""

import os
import pydicom
from pathlib import Path
from typing import List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DICOMLoader:
    """Loads DICOM files from directories or individual files"""

    def __init__(self):
        self.dicom_files = []
        self.loaded_datasets = []

    def load_from_directory(self, directory_path: str, recursive: bool = True) -> List[str]:
        """
        Load all DICOM files from a directory

        Args:
            directory_path: Path to the directory containing DICOM files
            recursive: If True, search subdirectories recursively

        Returns:
            List of paths to valid DICOM files
        """
        directory = Path(directory_path)

        if not directory.exists():
            logger.error(f"Directory does not exist: {directory_path}")
            return []

        pattern = "**/*" if recursive else "*"
        dicom_files = []

        for file_path in directory.glob(pattern):
            if file_path.is_file() and self._is_dicom_file(file_path):
                dicom_files.append(str(file_path))

        self.dicom_files.extend(dicom_files)
        logger.info(f"Found {len(dicom_files)} DICOM files in {directory_path}")

        return dicom_files

    def load_file(self, file_path: str) -> Optional[pydicom.Dataset]:
        """
        Load a single DICOM file

        Args:
            file_path: Path to the DICOM file

        Returns:
            pydicom.Dataset object or None if loading fails
        """
        try:
            dataset = pydicom.dcmread(file_path)
            self.loaded_datasets.append(dataset)
            logger.info(f"Successfully loaded: {file_path}")
            return dataset
        except Exception as e:
            logger.error(f"Error loading {file_path}: {str(e)}")
            return None

    def load_files(self, file_paths: List[str]) -> List[pydicom.Dataset]:
        """
        Load multiple DICOM files

        Args:
            file_paths: List of paths to DICOM files

        Returns:
            List of pydicom.Dataset objects
        """
        datasets = []

        for file_path in file_paths:
            dataset = self.load_file(file_path)
            if dataset is not None:
                datasets.append(dataset)

        return datasets

    def _is_dicom_file(self, file_path: Path) -> bool:
        """
        Check if a file is a valid DICOM file

        Args:
            file_path: Path to the file

        Returns:
            True if file is a valid DICOM file
        """
        try:
            # Try to read the file header
            pydicom.dcmread(file_path, stop_before_pixels=True)
            return True
        except:
            return False

    def get_file_count(self) -> int:
        """Get the number of DICOM files found"""
        return len(self.dicom_files)

    def clear(self):
        """Clear all loaded files and datasets"""
        self.dicom_files.clear()
        self.loaded_datasets.clear()
