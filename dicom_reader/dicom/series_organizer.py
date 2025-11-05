"""
DICOM Series Organizer
Organizes DICOM files into studies and series
"""

import pydicom
from typing import List, Dict
from collections import defaultdict
import logging

from .parser import DICOMParser

logger = logging.getLogger(__name__)


class DICOMSeries:
    """Represents a DICOM series with multiple instances"""

    def __init__(self, series_instance_uid: str):
        self.series_instance_uid = series_instance_uid
        self.series_number = None
        self.series_description = ""
        self.modality = ""
        self.instances = []
        self.datasets = []

    def add_instance(self, dataset: pydicom.Dataset):
        """Add an instance to the series"""
        self.datasets.append(dataset)

        # Update series info from first instance
        if len(self.datasets) == 1:
            series_info = DICOMParser.get_series_info(dataset)
            self.series_number = series_info['series_number']
            self.series_description = series_info['series_description']
            self.modality = series_info['modality']

    def sort_instances(self):
        """Sort instances by instance number or slice location"""
        try:
            # Try to sort by instance number
            self.datasets.sort(key=lambda d: int(d.get('InstanceNumber', 0)))
        except:
            try:
                # Try to sort by slice location
                self.datasets.sort(key=lambda d: float(d.get('SliceLocation', 0)))
            except:
                logger.warning(f"Could not sort series {self.series_instance_uid}")

    def get_instance_count(self) -> int:
        """Get the number of instances in this series"""
        return len(self.datasets)

    def __str__(self):
        return f"Series {self.series_number}: {self.series_description} ({self.modality}) - {self.get_instance_count()} images"


class DICOMStudy:
    """Represents a DICOM study with multiple series"""

    def __init__(self, study_instance_uid: str):
        self.study_instance_uid = study_instance_uid
        self.study_date = ""
        self.study_description = ""
        self.patient_name = ""
        self.patient_id = ""
        self.series_dict: Dict[str, DICOMSeries] = {}

    def add_dataset(self, dataset: pydicom.Dataset):
        """Add a dataset to the appropriate series"""
        # Update study info from first dataset
        if len(self.series_dict) == 0:
            study_info = DICOMParser.get_study_info(dataset)
            patient_info = DICOMParser.get_patient_info(dataset)
            self.study_date = study_info['study_date']
            self.study_description = study_info['study_description']
            self.patient_name = patient_info['patient_name']
            self.patient_id = patient_info['patient_id']

        # Get or create series
        series_uid = str(dataset.get('SeriesInstanceUID', ''))
        if series_uid not in self.series_dict:
            self.series_dict[series_uid] = DICOMSeries(series_uid)

        self.series_dict[series_uid].add_instance(dataset)

    def get_series_list(self) -> List[DICOMSeries]:
        """Get sorted list of series"""
        series_list = list(self.series_dict.values())
        series_list.sort(key=lambda s: s.series_number if s.series_number else 0)
        return series_list

    def get_series_count(self) -> int:
        """Get the number of series in this study"""
        return len(self.series_dict)

    def __str__(self):
        return f"Study: {self.study_description} ({self.study_date}) - {self.get_series_count()} series"


class SeriesOrganizer:
    """Organizes DICOM datasets into studies and series"""

    def __init__(self):
        self.studies_dict: Dict[str, DICOMStudy] = {}

    def add_datasets(self, datasets: List[pydicom.Dataset]):
        """
        Add multiple datasets and organize them into studies and series

        Args:
            datasets: List of pydicom.Dataset objects
        """
        for dataset in datasets:
            self.add_dataset(dataset)

    def add_dataset(self, dataset: pydicom.Dataset):
        """
        Add a single dataset

        Args:
            dataset: pydicom.Dataset object
        """
        # Get or create study
        study_uid = str(dataset.get('StudyInstanceUID', ''))

        if not study_uid:
            logger.warning("Dataset missing StudyInstanceUID, skipping")
            return

        if study_uid not in self.studies_dict:
            self.studies_dict[study_uid] = DICOMStudy(study_uid)

        self.studies_dict[study_uid].add_dataset(dataset)

    def get_studies_list(self) -> List[DICOMStudy]:
        """Get sorted list of studies"""
        studies_list = list(self.studies_dict.values())
        studies_list.sort(key=lambda s: s.study_date, reverse=True)
        return studies_list

    def sort_all_series(self):
        """Sort instances in all series"""
        for study in self.studies_dict.values():
            for series in study.series_dict.values():
                series.sort_instances()

    def get_total_studies(self) -> int:
        """Get total number of studies"""
        return len(self.studies_dict)

    def get_total_series(self) -> int:
        """Get total number of series across all studies"""
        return sum(study.get_series_count() for study in self.studies_dict.values())

    def get_total_instances(self) -> int:
        """Get total number of instances across all series"""
        total = 0
        for study in self.studies_dict.values():
            for series in study.series_dict.values():
                total += series.get_instance_count()
        return total

    def clear(self):
        """Clear all organized data"""
        self.studies_dict.clear()

    def get_summary(self) -> str:
        """Get a summary of organized data"""
        return (f"Organized: {self.get_total_studies()} studies, "
                f"{self.get_total_series()} series, "
                f"{self.get_total_instances()} instances")
