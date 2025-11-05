"""
DICOM Reader
A comprehensive DICOM file viewer with advanced features
"""

__version__ = '1.0.0'
__author__ = 'DICOM Reader Development Team'

from . import dicom
from . import gui
from . import processing
from . import database
from . import utils

__all__ = [
    'dicom',
    'gui',
    'processing',
    'database',
    'utils'
]
