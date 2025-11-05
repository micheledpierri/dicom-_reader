"""
Main GUI Window
The primary interface for the DICOM reader application
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QFileDialog, QSplitter, QTreeWidget,
                             QTreeWidgetItem, QStatusBar, QMenuBar, QMenu,
                             QAction, QMessageBox, QLabel, QProgressBar)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
import logging
import os

from ..dicom.loader import DICOMLoader
from ..dicom.series_organizer import SeriesOrganizer, DICOMStudy, DICOMSeries
from .viewer_widget import ViewerWidget
from .series_navigator import SeriesNavigator

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.dicom_loader = DICOMLoader()
        self.series_organizer = SeriesOrganizer()
        self.current_series = None

        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("DICOM Reader")
        self.setGeometry(100, 100, 1400, 900)

        # Create menu bar
        self.create_menu_bar()

        # Create main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)

        # Left panel - Study/Series browser
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)

        # Right panel - Image viewer
        self.viewer_widget = ViewerWidget()
        splitter.addWidget(self.viewer_widget)

        # Set initial sizes (30% left, 70% right)
        splitter.setSizes([400, 1000])

        main_layout.addWidget(splitter)

        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # Create progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('File')

        open_dir_action = QAction('Open Directory...', self)
        open_dir_action.setShortcut('Ctrl+O')
        open_dir_action.triggered.connect(self.open_directory)
        file_menu.addAction(open_dir_action)

        open_files_action = QAction('Open Files...', self)
        open_files_action.setShortcut('Ctrl+Shift+O')
        open_files_action.triggered.connect(self.open_files)
        file_menu.addAction(open_files_action)

        file_menu.addSeparator()

        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Tools menu
        tools_menu = menubar.addMenu('Tools')

        filters_action = QAction('Image Filters...', self)
        filters_action.triggered.connect(self.open_filters)
        tools_menu.addAction(filters_action)

        reconstruction_3d_action = QAction('3D Reconstruction...', self)
        reconstruction_3d_action.triggered.connect(self.open_3d_reconstruction)
        tools_menu.addAction(reconstruction_3d_action)

        # Database menu
        db_menu = menubar.addMenu('Database')

        add_to_db_action = QAction('Add to Database...', self)
        add_to_db_action.triggered.connect(self.add_to_database)
        db_menu.addAction(add_to_db_action)

        manage_db_action = QAction('Manage Database...', self)
        manage_db_action.triggered.connect(self.manage_database)
        db_menu.addAction(manage_db_action)

        # Help menu
        help_menu = menubar.addMenu('Help')

        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_left_panel(self) -> QWidget:
        """Create the left panel with study/series browser"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Buttons
        button_layout = QHBoxLayout()

        self.open_dir_btn = QPushButton("Open Directory")
        self.open_dir_btn.clicked.connect(self.open_directory)
        button_layout.addWidget(self.open_dir_btn)

        self.open_files_btn = QPushButton("Open Files")
        self.open_files_btn.clicked.connect(self.open_files)
        button_layout.addWidget(self.open_files_btn)

        layout.addLayout(button_layout)

        # Study/Series tree
        self.study_tree = QTreeWidget()
        self.study_tree.setHeaderLabels(["Studies and Series"])
        self.study_tree.itemClicked.connect(self.on_tree_item_clicked)
        layout.addWidget(self.study_tree)

        # Series navigator
        self.series_navigator = SeriesNavigator()
        self.series_navigator.series_changed.connect(self.on_series_changed)
        layout.addWidget(self.series_navigator)

        return panel

    def open_directory(self):
        """Open a directory containing DICOM files"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Directory Containing DICOM Files",
            os.path.expanduser("~")
        )

        if directory:
            self.load_dicom_directory(directory)

    def open_files(self):
        """Open individual DICOM files"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select DICOM Files",
            os.path.expanduser("~"),
            "DICOM Files (*.dcm *.dicom);;All Files (*)"
        )

        if files:
            self.load_dicom_files(files)

    def load_dicom_directory(self, directory: str):
        """Load DICOM files from directory"""
        self.status_bar.showMessage(f"Loading DICOM files from {directory}...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress

        try:
            # Clear previous data
            self.dicom_loader.clear()
            self.series_organizer.clear()
            self.study_tree.clear()

            # Load files
            file_paths = self.dicom_loader.load_from_directory(directory)

            if not file_paths:
                QMessageBox.warning(self, "No DICOM Files", "No DICOM files found in the selected directory.")
                self.status_bar.showMessage("Ready")
                self.progress_bar.setVisible(False)
                return

            # Load datasets
            datasets = self.dicom_loader.load_files(file_paths)

            # Organize into series
            self.series_organizer.add_datasets(datasets)
            self.series_organizer.sort_all_series()

            # Update UI
            self.populate_study_tree()

            summary = self.series_organizer.get_summary()
            self.status_bar.showMessage(f"Loaded: {summary}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading DICOM files: {str(e)}")
            logger.error(f"Error loading directory: {str(e)}", exc_info=True)
            self.status_bar.showMessage("Error loading files")

        finally:
            self.progress_bar.setVisible(False)

    def load_dicom_files(self, file_paths: list):
        """Load individual DICOM files"""
        self.status_bar.showMessage("Loading DICOM files...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)

        try:
            # Clear previous data
            self.dicom_loader.clear()
            self.series_organizer.clear()
            self.study_tree.clear()

            # Load datasets
            datasets = self.dicom_loader.load_files(file_paths)

            if not datasets:
                QMessageBox.warning(self, "No DICOM Files", "Could not load any valid DICOM files.")
                self.status_bar.showMessage("Ready")
                self.progress_bar.setVisible(False)
                return

            # Organize into series
            self.series_organizer.add_datasets(datasets)
            self.series_organizer.sort_all_series()

            # Update UI
            self.populate_study_tree()

            summary = self.series_organizer.get_summary()
            self.status_bar.showMessage(f"Loaded: {summary}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading DICOM files: {str(e)}")
            logger.error(f"Error loading files: {str(e)}", exc_info=True)
            self.status_bar.showMessage("Error loading files")

        finally:
            self.progress_bar.setVisible(False)

    def populate_study_tree(self):
        """Populate the study/series tree widget"""
        self.study_tree.clear()

        studies = self.series_organizer.get_studies_list()

        for study in studies:
            study_item = QTreeWidgetItem(self.study_tree)
            study_item.setText(0, str(study))
            study_item.setData(0, Qt.UserRole, study)

            series_list = study.get_series_list()
            for series in series_list:
                series_item = QTreeWidgetItem(study_item)
                series_item.setText(0, str(series))
                series_item.setData(0, Qt.UserRole, series)

        self.study_tree.expandAll()

    def on_tree_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle tree item click"""
        data = item.data(0, Qt.UserRole)

        if isinstance(data, DICOMSeries):
            self.load_series(data)
        elif isinstance(data, DICOMStudy):
            # Load first series of the study
            series_list = data.get_series_list()
            if series_list:
                self.load_series(series_list[0])

    def load_series(self, series: DICOMSeries):
        """Load a series into the viewer"""
        self.current_series = series
        self.viewer_widget.load_series(series)
        self.series_navigator.set_series(series)
        self.status_bar.showMessage(f"Loaded: {str(series)}")

    def on_series_changed(self, index: int):
        """Handle series navigation"""
        if self.current_series:
            self.viewer_widget.set_current_index(index)

    def open_filters(self):
        """Open the filters dialog"""
        # TODO: Implement filters dialog
        QMessageBox.information(self, "Filters", "Image filters feature will be implemented.")

    def open_3d_reconstruction(self):
        """Open the 3D reconstruction dialog"""
        # TODO: Implement 3D reconstruction
        QMessageBox.information(self, "3D Reconstruction", "3D reconstruction feature will be implemented.")

    def add_to_database(self):
        """Add current images to database"""
        # TODO: Implement database addition
        QMessageBox.information(self, "Database", "Add to database feature will be implemented.")

    def manage_database(self):
        """Open database management dialog"""
        # TODO: Implement database management
        QMessageBox.information(self, "Database", "Database management feature will be implemented.")

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About DICOM Reader",
            "DICOM Reader v1.0\n\n"
            "A comprehensive DICOM file viewer with advanced features:\n"
            "- Multi-series navigation\n"
            "- Cine mode playback\n"
            "- Image processing filters\n"
            "- 3D reconstruction\n"
            "- Local database management"
        )
