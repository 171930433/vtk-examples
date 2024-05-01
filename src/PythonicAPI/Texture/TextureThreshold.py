#!/usr/bin/env python3

# Modified from VTK/Filters/Texture/Testing/Python/textureThreshold.py.

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersCore import vtkStructuredGridOutlineFilter
from vtkmodules.vtkFiltersGeometry import vtkStructuredGridGeometryFilter
from vtkmodules.vtkFiltersTexture import vtkThresholdTextureCoords
from vtkmodules.vtkIOLegacy import vtkStructuredPointsReader
from vtkmodules.vtkIOParallel import vtkMultiBlockPLOT3DReader
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkCamera,
    vtkDataSetMapper,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer,
    vtkTexture
)


def main():
    data_fn1, data_fn2, texture_fn = get_program_parameters()

    colors = vtkNamedColors()

    # Read the data.
    pl3d = vtkMultiBlockPLOT3DReader(xyz_file_name=data_fn1, q_file_name=data_fn2,
                                     scalar_function_number=100, vector_function_number=202)
    pl3d.Update()
    output = pl3d.GetOutput().GetBlock(0)

    # Make the wall (floor).
    wall = vtkStructuredGridGeometryFilter(extent=(0, 100, 0, 0, 0, 100))
    wall_map = vtkPolyDataMapper(scalar_visibility=False)
    output >> wall >> wall_map
    wall_actor = vtkActor(mapper=wall_map)
    wall_actor.GetProperty().SetColor(colors.GetColor3d('PeachPuff'))

    # Make the fin (rear wall)
    fin = vtkStructuredGridGeometryFilter(extent=(0, 100, 0, 100, 0, 0))
    fin_map = vtkPolyDataMapper(scalar_visibility=False)
    output >> fin >> fin_map
    fin_actor = vtkActor(mapper=fin_map)
    fin_actor.property.color = colors.GetColor3d('DarkSlateGray')

    # Get the texture.
    tmap = vtkStructuredPointsReader()
    tmap.SetFileName(texture_fn)
    texture = vtkTexture(interpolate=False, repeat=False)
    tmap >> texture

    # Create the rendering window, renderer, and interactive renderer.
    ren = vtkRenderer(background=colors.GetColor3d('MistyRose'))
    ren_win = vtkRenderWindow(size=(512, 512), window_name='TextureThreshold')
    ren_win.AddRenderer(ren)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    # Make the planes to threshold and texture.
    # Define the extents of planes that we will use.
    plane_extents = [[10, 10, 0, 100, 0, 100],
                     [30, 30, 0, 100, 0, 100],
                     [35, 35, 0, 100, 0, 100]]
    # Now set up the pipeline.
    for i in range(0, len(plane_extents)):
        extent = plane_extents[i]
        plane = vtkStructuredGridGeometryFilter(extent=extent)
        thresh = vtkThresholdTextureCoords()
        # If you want an image similar to Fig 9-43(a) in the VTK textbook,
        # set thresh[i].ThresholdByUpper(1.5) for all planes.
        if i == 1:
            thresh.ThresholdByLower(1.5)
        elif i == 2:
            thresh.ThresholdBetween(1.5, 1.8)
        else:
            thresh.ThresholdByUpper(1.5)
        plane_map = vtkDataSetMapper(scalar_range=output.scalar_range)
        output >> plane >> thresh >> plane_map
        plane_actor = vtkActor(mapper=plane_map, texture=texture)
        # The slight transparency gives a nice effect.
        plane_actor.property.opacity = 0.999
        ren.AddActor(plane_actor)

    # Get an outline of the data set for context.
    outline = vtkStructuredGridOutlineFilter()
    outline_mapper = vtkPolyDataMapper()
    output >> outline >> outline_mapper
    outline_actor = vtkActor(mapper=outline_mapper)
    outline_prop = outline_actor.GetProperty()
    outline_prop.color = colors.GetColor3d('Black')

    # Add the remaining actors to the renderer, set the background and size.
    ren.AddActor(outline_actor)
    ren.AddActor(wall_actor)
    ren.AddActor(fin_actor)

    cam = vtkCamera()
    cam.clipping_range = (1.51176, 75.5879)
    cam.focal_point = (2.33749, 2.96739, 3.61023)
    cam.position = (10.8787, 5.27346, 15.8687)
    cam.view_angle = 30
    cam.view_up = (-0.0610856, 0.987798, -0.143262)
    ren.active_camera = cam

    iren.Initialize()
    iren.Start()


def get_program_parameters():
    import argparse
    description = 'Demonstrating texture thresholding applied to scalar data from a simulation of fluid flow.'
    epilogue = '''
    There are three planes cutting the blunt fin with different thresholds set. 
     From the left, the scalar threshold is set so that:
       1) Only data with a scalar value greater than or equal to 1.5 is shown.
       2) Only data with a scalar value less than or equal to 1.5 is shown.
       3) Only data with a scalar value between 1.5 and 1.8 inclusive is shown.
   '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('dataFn1', help='bluntfinxyz.bin.')
    parser.add_argument('dataFn2', help='bluntfinq.bin.')
    parser.add_argument('textureFn', help='texThres2.vtk')
    args = parser.parse_args()
    return args.dataFn1, args.dataFn2, args.textureFn


if __name__ == '__main__':
    main()
