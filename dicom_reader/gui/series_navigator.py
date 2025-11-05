"""
Series Navigator
Widget for navigating through images in a series
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QProgressBar)
from PyQt5.QtCore import Qt, pyqtSignal
import logging

from ..dicom.series_organizer import DICOMSeries

logger = logging.getLogger(__name__)


class SeriesNavigator(QWidget):
    """Widget for navigating through a DICOM series"""

    series_changed = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.current_series = None
        self.current_index = 0

        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)

        # Series info label
        self.series_label = QLabel("No series loaded")
        self.series_label.setAlignment(Qt.AlignCenter)
        self.series_label.setStyleSheet("QLabel { font-weight: bold; }")
        layout.addWidget(self.series_label)

        # Progress bar showing position in series
        progress_layout = QHBoxLayout()

        self.position_label = QLabel("0 / 0")
        self.position_label.setMinimumWidth(60)
        progress_layout.addWidget(self.position_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        progress_layout.addWidget(self.progress_bar)

        layout.addLayout(progress_layout)

        # Compact layout
        layout.setContentsMargins(5, 5, 5, 5)

    def set_series(self, series: DICOMSeries):
        """Set the current series"""
        self.current_series = series
        self.current_index = 0

        if series:
            self.series_label.setText(f"{series.series_description} ({series.modality})")
            self.progress_bar.setMaximum(series.get_instance_count())
            self.progress_bar.setValue(1)
            self.update_position_label()
        else:
            self.clear()

    def set_current_index(self, index: int):
        """Set the current image index"""
        if self.current_series and 0 <= index < self.current_series.get_instance_count():
            self.current_index = index
            self.progress_bar.setValue(index + 1)
            self.update_position_label()
            self.series_changed.emit(index)

    def update_position_label(self):
        """Update the position label"""
        if self.current_series:
            total = self.current_series.get_instance_count()
            current = self.current_index + 1
            self.position_label.setText(f"{current} / {total}")
        else:
            self.position_label.setText("0 / 0")

    def clear(self):
        """Clear the navigator"""
        self.series_label.setText("No series loaded")
        self.progress_bar.setMaximum(0)
        self.progress_bar.setValue(0)
        self.position_label.setText("0 / 0")
        self.current_series = None
        self.current_index = 0
