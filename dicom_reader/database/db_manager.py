"""
Database Manager
Handles all database operations for DICOM files
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional
import logging
import pydicom

from .models import Base, Patient, Study, Series, Instance
from ..dicom.parser import DICOMParser

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages the DICOM database"""

    def __init__(self, db_path: str = None):
        """
        Initialize database manager

        Args:
            db_path: Path to SQLite database file. If None, uses default location.
        """
        if db_path is None:
            # Use default location in user's home directory
            home_dir = os.path.expanduser("~")
            db_dir = os.path.join(home_dir, ".dicom_reader")
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, "dicom_database.db")

        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}')
        self.Session = sessionmaker(bind=self.engine)

        # Create tables if they don't exist
        Base.metadata.create_all(self.engine)

        logger.info(f"Database initialized at: {db_path}")

    def get_session(self) -> Session:
        """Get a new database session"""
        return self.Session()

    def add_dicom_file(self, file_path: str, dataset: pydicom.Dataset = None) -> bool:
        """
        Add a DICOM file to the database

        Args:
            file_path: Path to the DICOM file
            dataset: Pre-loaded pydicom.Dataset (optional)

        Returns:
            True if successful
        """
        session = self.get_session()

        try:
            # Load dataset if not provided
            if dataset is None:
                dataset = pydicom.dcmread(file_path)

            # Extract metadata
            patient_info = DICOMParser.get_patient_info(dataset)
            study_info = DICOMParser.get_study_info(dataset)
            series_info = DICOMParser.get_series_info(dataset)
            instance_info = DICOMParser.get_instance_info(dataset)
            image_info = DICOMParser.get_image_info(dataset)

            # Get or create patient
            patient = session.query(Patient).filter_by(
                patient_id=patient_info['patient_id']
            ).first()

            if not patient:
                patient = Patient(
                    patient_id=patient_info['patient_id'],
                    patient_name=patient_info['patient_name'],
                    patient_sex=patient_info['patient_sex'],
                    patient_birth_date=patient_info['patient_birth_date'],
                    patient_age=patient_info['patient_age']
                )
                session.add(patient)
                session.flush()

            # Get or create study
            study = session.query(Study).filter_by(
                study_instance_uid=study_info['study_instance_uid']
            ).first()

            if not study:
                study = Study(
                    study_instance_uid=study_info['study_instance_uid'],
                    patient_id=patient.id,
                    study_date=study_info['study_date'],
                    study_time=study_info['study_time'],
                    study_description=study_info['study_description'],
                    accession_number=study_info['accession_number']
                )
                session.add(study)
                session.flush()

            # Get or create series
            series = session.query(Series).filter_by(
                series_instance_uid=series_info['series_instance_uid']
            ).first()

            if not series:
                series = Series(
                    series_instance_uid=series_info['series_instance_uid'],
                    study_id=study.id,
                    series_number=series_info['series_number'],
                    series_description=series_info['series_description'],
                    modality=series_info['modality'],
                    series_date=series_info['series_date'],
                    series_time=series_info['series_time']
                )
                session.add(series)
                session.flush()

            # Check if instance already exists
            existing_instance = session.query(Instance).filter_by(
                sop_instance_uid=instance_info['sop_instance_uid']
            ).first()

            if existing_instance:
                # Update file path if different
                if existing_instance.file_path != file_path:
                    existing_instance.file_path = file_path
                    logger.info(f"Updated instance path: {instance_info['sop_instance_uid']}")
            else:
                # Create new instance
                instance = Instance(
                    sop_instance_uid=instance_info['sop_instance_uid'],
                    series_id=series.id,
                    instance_number=instance_info['instance_number'],
                    acquisition_number=instance_info['acquisition_number'],
                    file_path=file_path,
                    rows=image_info['rows'],
                    columns=image_info['columns'],
                    slice_location=image_info['slice_location'],
                    slice_thickness=image_info['slice_thickness']
                )
                session.add(instance)
                logger.info(f"Added instance: {instance_info['sop_instance_uid']}")

            session.commit()
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"Error adding DICOM file to database: {str(e)}", exc_info=True)
            return False

        finally:
            session.close()

    def add_dicom_files(self, file_paths: List[str]) -> int:
        """
        Add multiple DICOM files to the database

        Args:
            file_paths: List of paths to DICOM files

        Returns:
            Number of files successfully added
        """
        count = 0
        for file_path in file_paths:
            if self.add_dicom_file(file_path):
                count += 1
        return count

    def get_all_patients(self) -> List[Patient]:
        """Get all patients from database"""
        session = self.get_session()
        try:
            return session.query(Patient).all()
        finally:
            session.close()

    def get_patient_studies(self, patient_id: str) -> List[Study]:
        """Get all studies for a patient"""
        session = self.get_session()
        try:
            patient = session.query(Patient).filter_by(patient_id=patient_id).first()
            if patient:
                return patient.studies
            return []
        finally:
            session.close()

    def get_study_series(self, study_uid: str) -> List[Series]:
        """Get all series for a study"""
        session = self.get_session()
        try:
            study = session.query(Study).filter_by(study_instance_uid=study_uid).first()
            if study:
                return study.series
            return []
        finally:
            session.close()

    def get_series_instances(self, series_uid: str) -> List[Instance]:
        """Get all instances for a series"""
        session = self.get_session()
        try:
            series = session.query(Series).filter_by(series_instance_uid=series_uid).first()
            if series:
                return series.instances
            return []
        finally:
            session.close()

    def search_patients(self, search_term: str) -> List[Patient]:
        """
        Search patients by name or ID

        Args:
            search_term: Search term

        Returns:
            List of matching patients
        """
        session = self.get_session()
        try:
            return session.query(Patient).filter(
                (Patient.patient_name.like(f'%{search_term}%')) |
                (Patient.patient_id.like(f'%{search_term}%'))
            ).all()
        finally:
            session.close()

    def search_studies(self, search_term: str) -> List[Study]:
        """
        Search studies by description or accession number

        Args:
            search_term: Search term

        Returns:
            List of matching studies
        """
        session = self.get_session()
        try:
            return session.query(Study).filter(
                (Study.study_description.like(f'%{search_term}%')) |
                (Study.accession_number.like(f'%{search_term}%'))
            ).all()
        finally:
            session.close()

    def delete_patient(self, patient_id: str) -> bool:
        """
        Delete a patient and all associated data

        Args:
            patient_id: Patient ID

        Returns:
            True if successful
        """
        session = self.get_session()
        try:
            patient = session.query(Patient).filter_by(patient_id=patient_id).first()
            if patient:
                session.delete(patient)
                session.commit()
                logger.info(f"Deleted patient: {patient_id}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting patient: {str(e)}", exc_info=True)
            return False
        finally:
            session.close()

    def delete_study(self, study_uid: str) -> bool:
        """
        Delete a study and all associated data

        Args:
            study_uid: Study Instance UID

        Returns:
            True if successful
        """
        session = self.get_session()
        try:
            study = session.query(Study).filter_by(study_instance_uid=study_uid).first()
            if study:
                session.delete(study)
                session.commit()
                logger.info(f"Deleted study: {study_uid}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting study: {str(e)}", exc_info=True)
            return False
        finally:
            session.close()

    def get_database_stats(self) -> dict:
        """Get database statistics"""
        session = self.get_session()
        try:
            stats = {
                'patients': session.query(Patient).count(),
                'studies': session.query(Study).count(),
                'series': session.query(Series).count(),
                'instances': session.query(Instance).count()
            }
            return stats
        finally:
            session.close()

    def close(self):
        """Close database connection"""
        self.engine.dispose()
