"""
Image Viewer Widget
Displays DICOM images with navigation and manipulation controls
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QSlider, QSpinBox, QGroupBox,
                             QFormLayout, QCheckBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage
import numpy as np
from PIL import Image
import logging

from ..dicom.parser import DICOMParser
from ..dicom.series_organizer import DICOMSeries

logger = logging.getLogger(__name__)


class ViewerWidget(QWidget):
    """Widget for displaying DICOM images"""

    image_changed = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.current_series = None
        self.current_index = 0
        self.current_image = None
        self.window_center = None
        self.window_width = None
        self.brightness = 0
        self.contrast = 1.0

        # Cine mode
        self.cine_timer = QTimer()
        self.cine_timer.timeout.connect(self.next_image)
        self.cine_fps = 10
        self.is_playing = False

        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)

        # Image display area
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("QLabel { background-color: black; }")
        self.image_label.setMinimumSize(400, 400)
        self.image_label.setScaledContents(False)
        layout.addWidget(self.image_label, stretch=1)

        # Image info
        self.info_label = QLabel("No image loaded")
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)

        # Navigation controls
        nav_group = self.create_navigation_controls()
        layout.addWidget(nav_group)

        # Window/Level controls
        wl_group = self.create_window_level_controls()
        layout.addWidget(wl_group)

        # Cine controls
        cine_group = self.create_cine_controls()
        layout.addWidget(cine_group)

    def create_navigation_controls(self) -> QGroupBox:
        """Create navigation control widgets"""
        group = QGroupBox("Navigation")
        layout = QVBoxLayout()

        # Slider
        self.image_slider = QSlider(Qt.Horizontal)
        self.image_slider.setMinimum(0)
        self.image_slider.setMaximum(0)
        self.image_slider.valueChanged.connect(self.on_slider_changed)
        layout.addWidget(self.image_slider)

        # Buttons
        button_layout = QHBoxLayout()

        self.first_btn = QPushButton("First")
        self.first_btn.clicked.connect(self.first_image)
        button_layout.addWidget(self.first_btn)

        self.prev_btn = QPushButton("Previous")
        self.prev_btn.clicked.connect(self.previous_image)
        button_layout.addWidget(self.prev_btn)

        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.next_image)
        button_layout.addWidget(self.next_btn)

        self.last_btn = QPushButton("Last")
        self.last_btn.clicked.connect(self.last_image)
        button_layout.addWidget(self.last_btn)

        layout.addLayout(button_layout)

        group.setLayout(layout)
        return group

    def create_window_level_controls(self) -> QGroupBox:
        """Create window/level control widgets"""
        group = QGroupBox("Window/Level")
        layout = QFormLayout()

        # Window Center
        self.wc_slider = QSlider(Qt.Horizontal)
        self.wc_slider.setMinimum(-2000)
        self.wc_slider.setMaximum(2000)
        self.wc_slider.setValue(0)
        self.wc_slider.valueChanged.connect(self.on_window_changed)

        self.wc_spinbox = QSpinBox()
        self.wc_spinbox.setMinimum(-2000)
        self.wc_spinbox.setMaximum(2000)
        self.wc_spinbox.valueChanged.connect(self.wc_slider.setValue)
        self.wc_slider.valueChanged.connect(self.wc_spinbox.setValue)

        wc_layout = QHBoxLayout()
        wc_layout.addWidget(self.wc_slider)
        wc_layout.addWidget(self.wc_spinbox)
        layout.addRow("Window Center:", wc_layout)

        # Window Width
        self.ww_slider = QSlider(Qt.Horizontal)
        self.ww_slider.setMinimum(1)
        self.ww_slider.setMaximum(4000)
        self.ww_slider.setValue(400)
        self.ww_slider.valueChanged.connect(self.on_window_changed)

        self.ww_spinbox = QSpinBox()
        self.ww_spinbox.setMinimum(1)
        self.ww_spinbox.setMaximum(4000)
        self.ww_spinbox.valueChanged.connect(self.ww_slider.setValue)
        self.ww_slider.valueChanged.connect(self.ww_spinbox.setValue)

        ww_layout = QHBoxLayout()
        ww_layout.addWidget(self.ww_slider)
        ww_layout.addWidget(self.ww_spinbox)
        layout.addRow("Window Width:", ww_layout)

        # Reset button
        reset_btn = QPushButton("Reset Window/Level")
        reset_btn.clicked.connect(self.reset_window_level)
        layout.addRow(reset_btn)

        group.setLayout(layout)
        return group

    def create_cine_controls(self) -> QGroupBox:
        """Create cine mode control widgets"""
        group = QGroupBox("Cine Mode")
        layout = QHBoxLayout()

        self.play_btn = QPushButton("Play")
        self.play_btn.clicked.connect(self.toggle_cine)
        layout.addWidget(self.play_btn)

        layout.addWidget(QLabel("FPS:"))

        self.fps_spinbox = QSpinBox()
        self.fps_spinbox.setMinimum(1)
        self.fps_spinbox.setMaximum(60)
        self.fps_spinbox.setValue(10)
        self.fps_spinbox.valueChanged.connect(self.on_fps_changed)
        layout.addWidget(self.fps_spinbox)

        self.loop_checkbox = QCheckBox("Loop")
        self.loop_checkbox.setChecked(True)
        layout.addWidget(self.loop_checkbox)

        layout.addStretch()

        group.setLayout(layout)
        return group

    def load_series(self, series: DICOMSeries):
        """Load a DICOM series"""
        self.current_series = series
        self.current_index = 0

        if series.get_instance_count() > 0:
            self.image_slider.setMaximum(series.get_instance_count() - 1)
            self.image_slider.setValue(0)
            self.display_current_image()
        else:
            self.clear_display()

    def display_current_image(self):
        """Display the current image"""
        if not self.current_series or self.current_index >= self.current_series.get_instance_count():
            return

        try:
            dataset = self.current_series.datasets[self.current_index]

            # Get window/level values if not set
            if self.window_center is None or self.window_width is None:
                self.reset_window_level()

            # Get windowed image
            image_array = DICOMParser.get_window_level_image(
                dataset,
                self.window_center,
                self.window_width
            )

            if image_array is None:
                logger.error("Could not get image array")
                return

            # Convert to QPixmap
            pixmap = self.array_to_pixmap(image_array)

            # Scale to fit label while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(
                self.image_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            self.image_label.setPixmap(scaled_pixmap)

            # Update info
            instance_info = DICOMParser.get_instance_info(dataset)
            image_info = DICOMParser.get_image_info(dataset)

            info_text = (f"Image {self.current_index + 1} of {self.current_series.get_instance_count()} | "
                        f"Size: {image_info['columns']}x{image_info['rows']} | "
                        f"Instance: {instance_info['instance_number']}")

            self.info_label.setText(info_text)

            self.image_changed.emit(self.current_index)

        except Exception as e:
            logger.error(f"Error displaying image: {str(e)}", exc_info=True)

    def array_to_pixmap(self, array: np.ndarray) -> QPixmap:
        """Convert numpy array to QPixmap"""
        # Ensure array is uint8
        if array.dtype != np.uint8:
            array = array.astype(np.uint8)

        height, width = array.shape
        bytes_per_line = width

        # Create QImage
        if len(array.shape) == 2:  # Grayscale
            qimage = QImage(array.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
        else:
            qimage = QImage(array.data, width, height, bytes_per_line, QImage.Format_RGB888)

        return QPixmap.fromImage(qimage)

    def clear_display(self):
        """Clear the image display"""
        self.image_label.clear()
        self.image_label.setText("No image to display")
        self.info_label.setText("No image loaded")

    def set_current_index(self, index: int):
        """Set the current image index"""
        if self.current_series and 0 <= index < self.current_series.get_instance_count():
            self.current_index = index
            self.image_slider.setValue(index)
            self.display_current_image()

    def on_slider_changed(self, value: int):
        """Handle slider value change"""
        self.current_index = value
        self.display_current_image()

    def first_image(self):
        """Go to first image"""
        self.set_current_index(0)

    def previous_image(self):
        """Go to previous image"""
        if self.current_index > 0:
            self.set_current_index(self.current_index - 1)

    def next_image(self):
        """Go to next image"""
        if self.current_series:
            next_idx = self.current_index + 1
            if next_idx < self.current_series.get_instance_count():
                self.set_current_index(next_idx)
            elif self.loop_checkbox.isChecked() and self.is_playing:
                # Loop back to start in cine mode
                self.set_current_index(0)
            elif self.is_playing and not self.loop_checkbox.isChecked():
                # Stop playing if reached end and loop is disabled
                self.stop_cine()

    def last_image(self):
        """Go to last image"""
        if self.current_series:
            self.set_current_index(self.current_series.get_instance_count() - 1)

    def on_window_changed(self):
        """Handle window/level change"""
        self.window_center = self.wc_slider.value()
        self.window_width = self.ww_slider.value()
        self.display_current_image()

    def reset_window_level(self):
        """Reset window/level to default values"""
        if self.current_series and self.current_index < self.current_series.get_instance_count():
            dataset = self.current_series.datasets[self.current_index]

            # Get default window center and width
            wc = dataset.get('WindowCenter', None)
            ww = dataset.get('WindowWidth', None)

            if wc is not None:
                self.window_center = float(wc[0]) if isinstance(wc, (list, tuple)) else float(wc)
            else:
                # Use pixel array statistics
                pixel_array = DICOMParser.get_pixel_array(dataset)
                if pixel_array is not None:
                    self.window_center = (pixel_array.max() + pixel_array.min()) / 2
                else:
                    self.window_center = 0

            if ww is not None:
                self.window_width = float(ww[0]) if isinstance(ww, (list, tuple)) else float(ww)
            else:
                # Use pixel array statistics
                pixel_array = DICOMParser.get_pixel_array(dataset)
                if pixel_array is not None:
                    self.window_width = pixel_array.max() - pixel_array.min()
                else:
                    self.window_width = 400

            # Update sliders
            self.wc_slider.setValue(int(self.window_center))
            self.ww_slider.setValue(int(self.window_width))

            self.display_current_image()

    def toggle_cine(self):
        """Toggle cine mode playback"""
        if self.is_playing:
            self.stop_cine()
        else:
            self.start_cine()

    def start_cine(self):
        """Start cine mode playback"""
        if self.current_series and self.current_series.get_instance_count() > 1:
            self.is_playing = True
            self.play_btn.setText("Stop")
            interval = int(1000 / self.fps_spinbox.value())
            self.cine_timer.start(interval)

    def stop_cine(self):
        """Stop cine mode playback"""
        self.is_playing = False
        self.play_btn.setText("Play")
        self.cine_timer.stop()

    def on_fps_changed(self, fps: int):
        """Handle FPS change"""
        self.cine_fps = fps
        if self.is_playing:
            interval = int(1000 / fps)
            self.cine_timer.setInterval(interval)

    def resizeEvent(self, event):
        """Handle resize event"""
        super().resizeEvent(event)
        # Redisplay image to scale it properly
        if self.current_series:
            self.display_current_image()
