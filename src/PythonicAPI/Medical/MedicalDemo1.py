#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersCore import (
    vtkFlyingEdges3D,
    vtkMarchingCubes
)
from vtkmodules.vtkFiltersModeling import vtkOutlineFilter
from vtkmodules.vtkIOImage import vtkMetaImageReader
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkCamera,
    vtkPolyDataMapper,
    vtkProperty,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()

    file_name, use_flying_edges = get_program_parameters()

    colors.SetColor('SkinColor', 240, 184, 160, 255)
    colors.SetColor('BackfaceColor', 255, 229, 200, 255)
    colors.SetColor('BkgColor', 51, 77, 102, 255)

    # Create the renderer, the render window, and the interactor. The renderer
    # draws into the render window, the interactor enables mouse- and
    # keyboard-based interaction with the data within the render window.
    #
    # Set a background color for the renderer and set the name and
    # size of the render window (expressed in pixels).
    ren = vtkRenderer(background=colors.GetColor3d('BkgColor'))
    ren_win = vtkRenderWindow(size=(640, 480), window_name='MedicalDemo1')
    ren_win.AddRenderer(ren)

    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    reader = vtkMetaImageReader(file_name=file_name)

    # An isosurface, or contour value of 500 is known to correspond to the
    # skin of the patient.
    if use_flying_edges:
        skin_extractor = vtkFlyingEdges3D()
        skin_extractor.SetValue(0, 500)
    else:
        skin_extractor = vtkMarchingCubes()
        skin_extractor.SetValue(0, 500)

    skin_mapper = vtkPolyDataMapper(scalar_visibility=False)
    reader >> skin_extractor >> skin_mapper

    skin = vtkActor(mapper=skin_mapper)
    skin.property.diffuse_color = colors.GetColor3d('SkinColor')

    back_prop = vtkProperty()
    back_prop.diffuse_color = colors.GetColor3d('BackfaceColor')
    skin.backface_property = back_prop

    # An outline provides context around the data.
    #
    outline_data = vtkOutlineFilter()

    map_outline = vtkPolyDataMapper()
    reader >> outline_data >> map_outline

    outline = vtkActor(mapper=map_outline)
    outline.property.color = colors.GetColor3d('Black')

    # It is convenient to create an initial view of the data. The FocalPoint
    # and Position form a vector direction. Later on (ResetCamera() method)
    # this vector is used to position the camera to look at the data in
    # this direction.
    camera = vtkCamera(view_up=(0, 0, -1), position=(0, -1, 0), focal_point=(0, 0, 0))
    camera.ComputeViewPlaneNormal()
    camera.Azimuth(30.0)
    camera.Elevation(30.0)

    # Actors are added to the renderer. An initial camera view is created.
    # The Dolly() method moves the camera towards the FocalPoint,
    # thereby enlarging the image.
    ren.AddActor(outline)
    ren.AddActor(skin)
    ren.active_camera = camera
    ren.ResetCamera()
    camera.Dolly(1.5)

    # Note that when camera movement occurs (as it does in the Dolly()
    # method), the clipping planes often need adjusting. Clipping planes
    # consist of two planes: near and far along the view direction. The
    # near plane clips out objects in front of the plane the far plane
    # clips out objects behind the plane. This way only what is drawn
    # between the planes is actually rendered.
    ren.ResetCameraClippingRange()

    # Initialize the event loop and then start it.
    iren.Initialize()
    iren.Start()


def get_program_parameters():
    import argparse
    description = 'The skin extracted from a CT dataset of the head.'
    epilogue = '''
    Derived from VTK/Examples/Cxx/Medical1.cxx
    This example reads a volume dataset, extracts an isosurface that
     represents the skin and displays it.
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='FullHead.mhd.')
    parser.add_argument('-m', '--marching_cubes', action='store_false',
                        help='Use Marching Cubes instead of Flying Edges.')
    args = parser.parse_args()
    return args.filename, args.marching_cubes


if __name__ == '__main__':
    main()
