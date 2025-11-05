"""
Database Models
SQLAlchemy models for DICOM database
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Patient(Base):
    """Patient information"""
    __tablename__ = 'patients'

    id = Column(Integer, primary_key=True)
    patient_id = Column(String(64), unique=True, nullable=False, index=True)
    patient_name = Column(String(256))
    patient_sex = Column(String(16))
    patient_birth_date = Column(String(32))
    patient_age = Column(String(16))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    studies = relationship("Study", back_populates="patient", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Patient(id={self.patient_id}, name={self.patient_name})>"


class Study(Base):
    """Study information"""
    __tablename__ = 'studies'

    id = Column(Integer, primary_key=True)
    study_instance_uid = Column(String(128), unique=True, nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    study_date = Column(String(32))
    study_time = Column(String(32))
    study_description = Column(Text)
    accession_number = Column(String(64))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="studies")
    series = relationship("Series", back_populates="study", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Study(uid={self.study_instance_uid}, desc={self.study_description})>"


class Series(Base):
    """Series information"""
    __tablename__ = 'series'

    id = Column(Integer, primary_key=True)
    series_instance_uid = Column(String(128), unique=True, nullable=False, index=True)
    study_id = Column(Integer, ForeignKey('studies.id'), nullable=False)
    series_number = Column(Integer)
    series_description = Column(Text)
    modality = Column(String(16))
    series_date = Column(String(32))
    series_time = Column(String(32))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    study = relationship("Study", back_populates="series")
    instances = relationship("Instance", back_populates="series", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Series(uid={self.series_instance_uid}, desc={self.series_description})>"


class Instance(Base):
    """Instance (image) information"""
    __tablename__ = 'instances'

    id = Column(Integer, primary_key=True)
    sop_instance_uid = Column(String(128), unique=True, nullable=False, index=True)
    series_id = Column(Integer, ForeignKey('series.id'), nullable=False)
    instance_number = Column(Integer)
    acquisition_number = Column(Integer)
    file_path = Column(Text, nullable=False)

    # Image information
    rows = Column(Integer)
    columns = Column(Integer)
    slice_location = Column(Float)
    slice_thickness = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    series = relationship("Series", back_populates="instances")

    def __repr__(self):
        return f"<Instance(uid={self.sop_instance_uid}, path={self.file_path})>"
