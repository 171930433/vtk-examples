#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkLookupTable
from vtkmodules.vtkCommonDataModel import vtkPlane
from vtkmodules.vtkFiltersCore import (
    vtkContourFilter,
    vtkCutter,
    vtkPolyDataNormals,
    vtkStripper,
    vtkStructuredGridOutlineFilter,
    vtkTubeFilter
)
from vtkmodules.vtkFiltersExtraction import vtkExtractGrid
from vtkmodules.vtkIOParallel import vtkMultiBlockPLOT3DReader
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
    xyz_file, q_file = get_program_parameters()

    colors = vtkNamedColors()

    # Create pipeline. Read structured grid data.
    # file_name is an alias for xyz_file_name
    pl3d = vtkMultiBlockPLOT3DReader(xyz_file_name=xyz_file, q_file_name=q_file, scalar_function_number=100,
                                     vector_function_number=202)

    pl3d_output = pl3d.update().output.GetBlock(0)

    # A convenience, use this filter to limit data for experimentation.
    extract = vtkExtractGrid(voi=(1, 55, -1000, 1000, -1000, 1000))

    # The (implicit) plane is used to do the cutting.
    plane = vtkPlane(origin=(0, 4, 2), normal=(0, 1, 0))

    # The cutter is set up to process each contour value over all cells
    # (SetSortByToSortByCell). This results in an ordered output of polygons
    # which is key to the compositing.
    cutter = vtkCutter(cut_function=plane, generate_cut_scalars=False, sort_by=Cutter.SortBy.VTK_SORT_BY_CELL)

    clut = vtkLookupTable(hue_range=(0, 0.67))
    clut.Build()

    cutter_mapper = vtkPolyDataMapper(lookup_table=clut, scalar_range=(0.18, 0.7))
    pl3d_output >> extract >> cutter >> cutter_mapper

    cut = vtkActor(mapper=cutter_mapper)

    # Add in some surface geometry for interest.
    iso = vtkContourFilter()
    iso.SetValue(0, .22)

    normals = vtkPolyDataNormals(feature_angle=60)

    iso_mapper = vtkPolyDataMapper(scalar_visibility=False)
    pl3d_output >> iso >> normals >> iso_mapper

    iso_property = vtkProperty(diffuse_color=colors.GetColor3d('Tomato'),
                               specular_color=colors.GetColor3d('White'),
                               diffuse=0.8, specular=0.5, specular_power=30)

    iso_actor = vtkActor(mapper=iso_mapper)
    iso_actor.property = iso_property

    outline = vtkStructuredGridOutlineFilter()
    pl3d_output >> outline

    outline_strip = vtkStripper()
    outline >> outline_strip

    outline_tubes = vtkTubeFilter(radius=0.1)
    outline >> outline_tubes
    outline_strip >> outline_tubes

    outline_mapper = vtkPolyDataMapper()
    outline_tubes >> outline_mapper

    outline_actor = vtkActor(mapper=outline_mapper)
    outline_actor.property.color = colors.GetColor3d('Banana')

    # Create the RenderWindow, Renderer and Interactor.
    ren = vtkRenderer(background=colors.GetColor3d('SlateGray'))
    ren_win = vtkRenderWindow(size=(640, 480), window_name='PseudoVolumeRendering')
    ren_win.AddRenderer(ren)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    # Add the actors to the renderer, set the background and size.
    ren.AddActor(outline_actor)
    ren.AddActor(iso_actor)
    iso_actor.visibility = True
    ren.AddActor(cut)

    n = 20
    opacity = 1.0 / float(n) * 5.0
    cut.property.opacity = 1

    camera = vtkCamera(clipping_range=(3.95297, 50), focal_point=(9.71821, 0.458166, 29.3999),
                       position=(2.7439, -37.3196, 38.7167), view_up=(-0.16123, 0.264271, 0.950876))
    camera.ComputeViewPlaneNormal()
    ren.active_camera = camera

    # Cut: generates n cut planes normal to camera's view plane.
    plane.normal = camera.view_plane_normal
    plane.origin = camera.focal_point
    cutter.GenerateValues(n, -5, 5)
    clut.alpha_range = (opacity, opacity)
    ren_win.Render()

    iren.Start()


def get_program_parameters():
    import argparse
    description = 'Perform psuedo volume rendering in a structured grid by compositing translucent cut planes.'
    epilogue = '''
    This same trick can be used for unstructured grids.
    Note that for better results, more planes can be created.
    Also, if your data is vtkImageData, there are much faster
     methods for volume rendering.
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename1', help='combxyz.bin.')
    parser.add_argument('filename2', help='combq.bin.')
    args = parser.parse_args()
    return args.filename1, args.filename2


@dataclass(frozen=True)
class Cutter:
    @dataclass(frozen=True)
    class SortBy:
        VTK_SORT_BY_VALUE: int = 0
        VTK_SORT_BY_CELL: int = 1


if __name__ == '__main__':
    main()
