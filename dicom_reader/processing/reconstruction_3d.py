"""
3D Reconstruction Module
Performs 3D volume reconstruction and rendering from DICOM series
"""

import numpy as np
import vtk
from vtk.util import numpy_support
import logging
from typing import List, Optional, Tuple

from ..dicom.series_organizer import DICOMSeries
from ..dicom.parser import DICOMParser

logger = logging.getLogger(__name__)


class VolumeReconstructor:
    """Handles 3D volume reconstruction from DICOM series"""

    def __init__(self):
        self.volume_data = None
        self.vtk_image_data = None
        self.spacing = (1.0, 1.0, 1.0)
        self.origin = (0.0, 0.0, 0.0)

    def reconstruct_from_series(self, series: DICOMSeries) -> bool:
        """
        Reconstruct 3D volume from a DICOM series

        Args:
            series: DICOMSeries object containing the images

        Returns:
            True if reconstruction was successful
        """
        try:
            if series.get_instance_count() < 2:
                logger.warning("Need at least 2 slices for 3D reconstruction")
                return False

            # Sort instances
            series.sort_instances()

            # Get all pixel arrays
            slices = []
            for dataset in series.datasets:
                pixel_array = DICOMParser.get_pixel_array(dataset)
                if pixel_array is not None:
                    slices.append(pixel_array)

            if not slices:
                logger.error("No valid pixel data found")
                return False

            # Stack slices into 3D volume
            self.volume_data = np.stack(slices, axis=0)

            # Get spacing information
            self._extract_spacing(series.datasets[0])

            # Create VTK image data
            self._create_vtk_image_data()

            logger.info(f"3D volume reconstructed: shape={self.volume_data.shape}")
            return True

        except Exception as e:
            logger.error(f"Error reconstructing volume: {str(e)}", exc_info=True)
            return False

    def _extract_spacing(self, dataset):
        """Extract voxel spacing from DICOM dataset"""
        try:
            # Get pixel spacing (row, column)
            pixel_spacing = dataset.get('PixelSpacing', [1.0, 1.0])
            row_spacing = float(pixel_spacing[0])
            col_spacing = float(pixel_spacing[1])

            # Get slice thickness
            slice_thickness = float(dataset.get('SliceThickness', 1.0))

            # VTK uses (x, y, z) ordering
            self.spacing = (col_spacing, row_spacing, slice_thickness)

            # Get image position
            image_position = dataset.get('ImagePositionPatient', [0.0, 0.0, 0.0])
            self.origin = tuple(float(x) for x in image_position)

        except Exception as e:
            logger.warning(f"Could not extract spacing info: {str(e)}")
            self.spacing = (1.0, 1.0, 1.0)
            self.origin = (0.0, 0.0, 0.0)

    def _create_vtk_image_data(self):
        """Create VTK image data from numpy array"""
        # Convert numpy array to VTK array
        vtk_array = numpy_support.numpy_to_vtk(
            self.volume_data.ravel(),
            deep=True,
            array_type=vtk.VTK_FLOAT
        )

        # Create VTK image data
        self.vtk_image_data = vtk.vtkImageData()
        self.vtk_image_data.SetDimensions(
            self.volume_data.shape[2],  # x
            self.volume_data.shape[1],  # y
            self.volume_data.shape[0]   # z
        )
        self.vtk_image_data.SetSpacing(self.spacing)
        self.vtk_image_data.SetOrigin(self.origin)
        self.vtk_image_data.GetPointData().SetScalars(vtk_array)

    def get_volume_shape(self) -> Optional[Tuple[int, int, int]]:
        """Get the shape of the reconstructed volume"""
        if self.volume_data is not None:
            return self.volume_data.shape
        return None

    def get_vtk_image_data(self) -> Optional[vtk.vtkImageData]:
        """Get the VTK image data for rendering"""
        return self.vtk_image_data


class VolumeRenderer:
    """Handles 3D volume rendering using VTK"""

    def __init__(self):
        self.renderer = vtk.vtkRenderer()
        self.render_window = vtk.vtkRenderWindow()
        self.interactor = vtk.vtkRenderWindowInteractor()

        self.render_window.AddRenderer(self.renderer)
        self.interactor.SetRenderWindow(self.render_window)

        # Volume properties
        self.volume = None
        self.volume_mapper = None
        self.volume_property = None

    def setup_volume_rendering(self, image_data: vtk.vtkImageData):
        """
        Setup volume rendering pipeline

        Args:
            image_data: VTK image data to render
        """
        # Create volume mapper
        self.volume_mapper = vtk.vtkGPUVolumeRayCastMapper()
        self.volume_mapper.SetInputData(image_data)

        # Create volume property
        self.volume_property = vtk.vtkVolumeProperty()
        self.volume_property.ShadeOn()
        self.volume_property.SetInterpolationTypeToLinear()

        # Create transfer functions
        self._create_default_transfer_functions(image_data)

        # Create volume
        self.volume = vtk.vtkVolume()
        self.volume.SetMapper(self.volume_mapper)
        self.volume.SetProperty(self.volume_property)

        # Add to renderer
        self.renderer.AddVolume(self.volume)
        self.renderer.SetBackground(0.1, 0.1, 0.1)
        self.renderer.ResetCamera()

    def _create_default_transfer_functions(self, image_data: vtk.vtkImageData):
        """Create default color and opacity transfer functions"""
        # Get scalar range
        scalar_range = image_data.GetScalarRange()

        # Color transfer function (grayscale)
        color_func = vtk.vtkColorTransferFunction()
        color_func.AddRGBPoint(scalar_range[0], 0.0, 0.0, 0.0)
        color_func.AddRGBPoint(scalar_range[1], 1.0, 1.0, 1.0)

        # Opacity transfer function
        opacity_func = vtk.vtkPiecewiseFunction()
        opacity_func.AddPoint(scalar_range[0], 0.0)
        opacity_func.AddPoint(scalar_range[0] + (scalar_range[1] - scalar_range[0]) * 0.2, 0.0)
        opacity_func.AddPoint(scalar_range[0] + (scalar_range[1] - scalar_range[0]) * 0.5, 0.5)
        opacity_func.AddPoint(scalar_range[1], 1.0)

        # Gradient opacity
        gradient_func = vtk.vtkPiecewiseFunction()
        gradient_func.AddPoint(0, 0.0)
        gradient_func.AddPoint(90, 0.5)
        gradient_func.AddPoint(100, 1.0)

        self.volume_property.SetColor(color_func)
        self.volume_property.SetScalarOpacity(opacity_func)
        self.volume_property.SetGradientOpacity(gradient_func)

    def set_bone_preset(self):
        """Apply bone rendering preset"""
        if self.volume_property is None:
            return

        color_func = vtk.vtkColorTransferFunction()
        color_func.AddRGBPoint(-3024, 0, 0, 0)
        color_func.AddRGBPoint(-16, 0.73, 0.25, 0.30)
        color_func.AddRGBPoint(641, 0.90, 0.82, 0.56)
        color_func.AddRGBPoint(3071, 1, 1, 1)

        opacity_func = vtk.vtkPiecewiseFunction()
        opacity_func.AddPoint(-3024, 0)
        opacity_func.AddPoint(-16, 0)
        opacity_func.AddPoint(641, 0.72)
        opacity_func.AddPoint(3071, 0.72)

        self.volume_property.SetColor(color_func)
        self.volume_property.SetScalarOpacity(opacity_func)

    def set_soft_tissue_preset(self):
        """Apply soft tissue rendering preset"""
        if self.volume_property is None:
            return

        color_func = vtk.vtkColorTransferFunction()
        color_func.AddRGBPoint(-3024, 0, 0, 0)
        color_func.AddRGBPoint(-1000, 0.62, 0.36, 0.18)
        color_func.AddRGBPoint(-500, 0.88, 0.60, 0.29)
        color_func.AddRGBPoint(3071, 0.83, 0.66, 1)

        opacity_func = vtk.vtkPiecewiseFunction()
        opacity_func.AddPoint(-3024, 0)
        opacity_func.AddPoint(-1000, 0)
        opacity_func.AddPoint(-500, 1.0)
        opacity_func.AddPoint(3071, 1.0)

        self.volume_property.SetColor(color_func)
        self.volume_property.SetScalarOpacity(opacity_func)

    def set_mip_rendering(self):
        """Set Maximum Intensity Projection rendering"""
        if self.volume_mapper:
            self.volume_mapper.SetBlendModeToMaximumIntensity()

    def set_composite_rendering(self):
        """Set composite (standard) rendering"""
        if self.volume_mapper:
            self.volume_mapper.SetBlendModeToComposite()

    def render(self):
        """Render the volume"""
        self.render_window.Render()

    def start_interaction(self):
        """Start the interactive viewer"""
        self.interactor.Start()

    def get_render_window(self) -> vtk.vtkRenderWindow:
        """Get the render window for embedding in Qt"""
        return self.render_window


class MPRReconstructor:
    """Multi-Planar Reconstruction for creating orthogonal views"""

    def __init__(self, volume_data: np.ndarray):
        self.volume_data = volume_data

    def get_axial_slice(self, z_index: int) -> Optional[np.ndarray]:
        """Get axial slice at given z index"""
        if 0 <= z_index < self.volume_data.shape[0]:
            return self.volume_data[z_index, :, :]
        return None

    def get_coronal_slice(self, y_index: int) -> Optional[np.ndarray]:
        """Get coronal slice at given y index"""
        if 0 <= y_index < self.volume_data.shape[1]:
            return self.volume_data[:, y_index, :]
        return None

    def get_sagittal_slice(self, x_index: int) -> Optional[np.ndarray]:
        """Get sagittal slice at given x index"""
        if 0 <= x_index < self.volume_data.shape[2]:
            return self.volume_data[:, :, x_index]
        return None

    def get_oblique_slice(self, point: Tuple[float, float, float],
                         normal: Tuple[float, float, float],
                         size: Tuple[int, int] = (256, 256)) -> np.ndarray:
        """
        Get oblique slice through the volume

        Args:
            point: Point on the slice plane
            normal: Normal vector of the slice plane
            size: Output slice size

        Returns:
            Oblique slice image
        """
        # This is a simplified implementation
        # A complete implementation would use proper 3D interpolation
        logger.warning("Oblique slicing not fully implemented")
        return np.zeros(size, dtype=self.volume_data.dtype)
