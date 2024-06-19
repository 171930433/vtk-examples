#!/usr/bin/env python

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import VTK_DOUBLE
from vtkmodules.vtkCommonDataModel import vtkImageData
from vtkmodules.vtkFiltersGeometry import vtkImageDataGeometryFilter
from vtkmodules.vtkIOXML import (
    vtkXMLImageDataReader,
    vtkXMLImageDataWriter
)
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def get_program_parameters():
    import argparse
    description = 'Generate image data, edit data points, store and reload it.'
    epilogue = '''
   '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue)
    parser.add_argument('filename', help='A required vtk filename, e.g. writeImageData.vti.', nargs='?',
                        const='writeImageData.vti',
                        type=str, default='writeImageData.vti')
    args = parser.parse_args()
    return args.filename


def main():
    colors = vtkNamedColors()

    filename = get_program_parameters()

    image_data = vtkImageData(dimensions=(3, 4, 5))
    image_data.AllocateScalars(VTK_DOUBLE, 1)

    dims = image_data.GetDimensions()

    # Fill every entry of the image data with '2.0'.
    for z in range(dims[2]):
        for y in range(dims[1]):
            for x in range(dims[0]):
                image_data.SetScalarComponentFromDouble(x, y, z, 0, 2.0)

    writer = vtkXMLImageDataWriter(file_name=filename, input_data=image_data)
    writer.Write()

    # Read the file (to test that it was written correctly).
    reader = vtkXMLImageDataReader(file_name=filename)

    # Convert the image to a polydata
    image_data_geometry_filter = vtkImageDataGeometryFilter()

    mapper = vtkPolyDataMapper()
    reader >> image_data_geometry_filter >> mapper

    actor = vtkActor(mapper=mapper)
    actor.property.point_size = 3

    # Setup rendering
    renderer = vtkRenderer(background=colors.GetColor3d('White'))
    render_window = vtkRenderWindow(window_name='WriteReadVtkImageData')
    render_window.AddRenderer(renderer)
    render_window_interactor = vtkRenderWindowInteractor()
    render_window_interactor.render_window = render_window

    renderer.AddActor(actor)
    renderer.ResetCamera()

    render_window_interactor.Initialize()
    render_window_interactor.Start()


if __name__ == '__main__':
    main()
