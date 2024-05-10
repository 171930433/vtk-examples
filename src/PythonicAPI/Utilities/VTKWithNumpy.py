# An example from scipy cookbook demonstrating the use of numpy arrays in vtk

from dataclasses import dataclass

import numpy as np
# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import vtkPiecewiseFunction
from vtkmodules.vtkIOImage import vtkImageImport
from vtkmodules.vtkRenderingCore import (
    vtkColorTransferFunction,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer,
    vtkVolume,
    vtkVolumeProperty
)
from vtkmodules.vtkRenderingVolume import vtkFixedPointVolumeRayCastMapper
# noinspection PyUnresolvedReferences
from vtkmodules.vtkRenderingVolumeOpenGL2 import vtkOpenGLRayCastImageDisplayHelper


def main():
    colors = vtkNamedColors()

    # We begin by creating the data we want to render.
    # For this tutorial, we create a 3D-image containing three overlapping cubes.
    # This data can of course easily be replaced by data from a medical CT-scan
    #  or anything else three-dimensional.
    # The only limit is that the data must be reduced to unsigned 8-bit or 16-bit integers.
    data_matrix = np.zeros([75, 75, 75], dtype=np.uint8)
    data_matrix[0:35, 0:35, 0:35] = 50
    data_matrix[25:55, 25:55, 25:55] = 100
    data_matrix[45:74, 45:74, 45:74] = 150

    # For VTK to be able to use the data, it must be stored as a VTK-image.
    #  This can be done by the vtkImageImport-class which imports raw data and stores it.
    data_importer = vtkImageImport(data_scalar_type=ImageImport.DataScalarType.VTK_UNSIGNED_CHAR,
                                   number_of_scalar_components=1,
                                   data_extent=(0, 74, 0, 74, 0, 74),
                                   whole_extent=(0, 74, 0, 74, 0, 74)
                                   )
    # The previously created array is converted to a string of chars and imported.
    data_string = data_matrix.tobytes()
    data_importer.CopyImportVoidPointer(data_string, len(data_string))

    # Note: The data scalar type, number of scalar components, data extent and whole extent
    #  can now be set when the class is initialized.
    # The type of the newly imported data is set to unsigned char (uint8)
    # data_importer.SetDataScalarTypeToUnsignedChar()
    # Because the data that is imported only contains an intensity value
    #  (it isn't RGB-coded or something similar), the importer must be told this is the case.
    # data_importer.SetNumberOfScalarComponents(1)
    # The following two functions describe how the data is stored and the dimensions of the array it is stored in.
    #  For this simple case, all axes are of length 75 and begins with the first element.
    #  For other data, this is probably not the case.
    # I have to admit however, that I honestly don't know the difference between SetDataExtent()
    #  and SetWholeExtent() although VTK complains if not both are used.
    # data_importer.SetDataExtent(0, 74, 0, 74, 0, 74)
    # data_importer.SetWholeExtent(0, 74, 0, 74, 0, 74)

    # The following class is used to store transparency-values for later retrival.
    # In our case, we want the value 0 to be completely opaque whereas the
    #  three different cubes are given different transparency-values to show how it works.
    alpha_channel_func = vtkPiecewiseFunction()
    alpha_channel_func.AddPoint(0, 0.0)
    alpha_channel_func.AddPoint(50, 0.05)
    alpha_channel_func.AddPoint(100, 0.1)
    alpha_channel_func.AddPoint(150, 0.2)

    # This class stores color data and can create color tables from a few color points.
    #  For this demo, we want the three cubes to be of the colors red green and blue.
    color_func = vtkColorTransferFunction()
    color_func.AddRGBPoint(50, 1.0, 0.0, 0.0)
    color_func.AddRGBPoint(100, 0.0, 1.0, 0.0)
    color_func.AddRGBPoint(150, 0.0, 0.0, 1.0)

    # The previous two classes stored properties.
    #  Because we want to apply these properties to the volume we want to render,
    # we have to store them in a class that stores volume properties.
    volume_property = vtkVolumeProperty(color=color_func, scalar_opacity=alpha_channel_func)

    volume_mapper = vtkFixedPointVolumeRayCastMapper()
    data_importer >> volume_mapper

    # The class vtkVolume is used to pair the previously declared volume as well as the properties
    #  to be used when rendering that volume.
    volume = vtkVolume(mapper=volume_mapper, property=volume_property)

    # With almost everything else ready, it's time to initialize the renderer and window,
    #  as well as creating a method for exiting the application
    renderer = vtkRenderer(background=colors.GetColor3d('MistyRose'))
    # Set the window size and name.
    render_win = vtkRenderWindow(size=(400, 400), window_name='VTKWithNumpy')
    render_win.AddRenderer(renderer)
    render_interactor = vtkRenderWindowInteractor()
    render_interactor.render_window = render_win

    # We add the volume to the renderer ...
    renderer.AddVolume(volume)

    # A simple function to be called when the user decides to quit the application.
    def exit_check(obj, event):
        if obj.GetEventPending() != 0:
            obj.SetAbortRender(1)

    # Tell the application to use the function as an exit check.
    render_win.AddObserver('AbortCheckEvent', exit_check)

    render_interactor.Initialize()
    # Because nothing will be rendered without any input, we order the first render manually
    #  before control is handed over to the main-loop.
    render_win.Render()
    render_interactor.Start()


@dataclass(frozen=True)
class ImageImport:
    @dataclass(frozen=True)
    class DataScalarType:
        VTK_UNSIGNED_CHAR: int = 3
        VTK_SHORT: int = 4
        VTK_UNSIGNED_SHORT: int = 5
        VTK_INT: int = 6
        VTK_FLOAT: int = 10
        VTK_DOUBLE: int = 11


if __name__ == '__main__':
    main()
