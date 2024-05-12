#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersCore import (
    vtkContourFilter,
    vtkFlyingEdges2D
)
from vtkmodules.vtkFiltersModeling import vtkOutlineFilter
from vtkmodules.vtkIOImage import vtkMetaImageReader
from vtkmodules.vtkImagingCore import vtkExtractVOI
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    file_name, use_contouring = get_program_parameters()
    if use_contouring:
        print('Using vtkContourFilter.')
    else:
        print('Using vtkFlyingEdges2D.')

    colors = vtkNamedColors()

    # Create the RenderWindow, Renderer and Interactor.
    ren = vtkRenderer(background=colors.GetColor3d('SlateGray'))
    ren_win = vtkRenderWindow(size=(640, 640), window_name='FlyingHeadSlice')
    ren_win.AddRenderer(ren)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    # Create the pipeline.
    reader = vtkMetaImageReader(file_name=file_name)
    # reader.SetFileName(file_name)
    reader.update()

    extract_voi = vtkExtractVOI(voi=(0, 255, 0, 255, 45, 45))
    p = reader >> extract_voi
    # This is the full scalar range.
    # scalar_range = p.update().output.scalar_range
    # This range matches the image.
    scalar_range = (500, 1150)
    # print(scalar_range)

    contour = vtkContourFilter()
    flying_edges = vtkFlyingEdges2D()
    iso_mapper = vtkPolyDataMapper(scalar_range=scalar_range, scalar_visibility=True)
    if use_contouring:
        contour.GenerateValues(12, scalar_range)
        p >> contour >> iso_mapper
    else:
        flying_edges.GenerateValues(12, scalar_range)
        p >> flying_edges >> iso_mapper

    iso_actor = vtkActor(mapper=iso_mapper)

    outline = vtkOutlineFilter()
    outline_mapper = vtkPolyDataMapper()
    p >> outline >> outline_mapper
    outline_actor = vtkActor(mapper=outline_mapper)
    outline_actor.property.color = colors.GetColor3d('Wheat')

    # Add the actors to the renderer, set the background and size.
    ren.AddActor(outline_actor)
    ren.AddActor(iso_actor)

    ren.ResetCamera()
    ren.active_camera.Dolly(1.4)
    ren.ResetCameraClippingRange()

    ren_win.Render()

    iren.Start()


def get_program_parameters():
    import argparse
    description = 'Either vtkFlyingEdges2D or vtkContourFilter is used to generate contour lines.'
    epilogue = '''
    Generate 2D contour lines, corresponding to tissue density, on one CT slice through the head.
    The contour lines are colored by the tissue density.
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='FullHead.mhd.')
    parser.add_argument('-c', '--useContouring', action='store_true',
                        help='Use vtkContourFilter instead of vtkFlyingEdges2D.')
    args = parser.parse_args()
    return args.filename, args.useContouring


if __name__ == '__main__':
    main()
