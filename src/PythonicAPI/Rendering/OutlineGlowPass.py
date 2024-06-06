#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersSources import vtkArrowSource
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)
from vtkmodules.vtkRenderingOpenGL2 import (
    vtkOutlineGlowPass,
    vtkRenderStepsPass
)


def get_program_parameters():
    import argparse
    description = 'How to render an object in a scene with a glowing outline.'
    epilogue = '''
Parts of a scene are highlighted by applying the render pass to a layered renderer
 on top of the main scene. For optimal results, actors that form the outline
 should be brightly colored with lighting disabled. The outline will have the
 color of the actors. There is only one outline around all objects rendered by the delegate.

When combined with layered renderers, this creates a very visible highlight without
 altering the highlighted object.
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.parse_args()
    return


def main():
    get_program_parameters()

    colors = vtkNamedColors()

    # Set up the renderers.
    # One for the object and the other for the outline.
    renderer = vtkRenderer(background=colors.GetColor3d('DarkSlateGray'),
                           background2=colors.GetColor3d('DarkSlateBlue'),
                           gradient_background=True)
    renderer_outline = vtkRenderer(layer=1)

    ren_win = vtkRenderWindow(size=(600, 600), multi_samples=0, window_name='OutlineGlowPass', number_of_layers=2)
    ren_win.AddRenderer(renderer_outline)
    ren_win.AddRenderer(renderer)

    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    # Create an arrow.
    arrow_source = vtkArrowSource()

    # Create mapper and actor for the main renderer.
    cone_mapper_main = vtkPolyDataMapper()
    cone_mapper_main.SetInputConnection(arrow_source.GetOutputPort())
    arrow_source >> cone_mapper_main

    cone_actor_main = vtkActor(mapper=cone_mapper_main)
    cone_actor_main.property.diffuse_color = colors.GetColor3d('LimeGreen')

    renderer.AddActor(cone_actor_main)

    # Let's make the outline glow!
    # Create the render pass.
    basic_passes = vtkRenderStepsPass()
    glow_pass = vtkOutlineGlowPass(delegate_pass=basic_passes)

    # Apply the render pass to the highlight renderer.
    renderer_outline.SetPass(glow_pass)

    # Create mapper and actor for the outline.
    cone_mapper_outline = vtkPolyDataMapper()
    arrow_source >> cone_mapper_outline

    cone_actor_outline = vtkActor(mapper=cone_mapper_outline)
    cone_actor_outline.property.color = colors.GetColor3d('Magenta')
    cone_actor_outline.property.LightingOff()

    renderer_outline.AddActor(cone_actor_outline)

    renderer.ResetCamera()
    camera = renderer.active_camera
    camera.Roll(45.0)
    camera.Azimuth(-30.0)
    camera.Elevation(-15.0)
    renderer.ResetCamera()
    # Now set the active camera for the outline.
    renderer_outline.active_camera = camera

    ren_win.Render()

    iren.Start()


if __name__ == '__main__':
    main()
