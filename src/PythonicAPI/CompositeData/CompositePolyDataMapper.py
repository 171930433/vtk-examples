#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import vtkMultiBlockDataSet
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkCompositeDataDisplayAttributes,
    vtkCompositePolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()

    # Create Sphere 1.
    sphere1 = vtkSphereSource(radius=3, center=(0, 0, 0))
    sphere1.update()

    # Create Sphere 2.
    sphere2 = vtkSphereSource(radius=2, center=(2, 0, 0))
    sphere2.update()

    # Leave block 1 as NULL.  NULL blocks are valid and should be handled by
    # algorithms that process multiblock datasets.  Especially when
    # running in parallel where the blocks are owned by other processes.
    mbds = vtkMultiBlockDataSet(number_of_blocks=3)
    mbds.SetBlock(0, sphere1.output)
    mbds.SetBlock(2, sphere2.output)

    # You can use the vtkCompositeDataDisplayAttributes to set the color,
    # opacity and visibiliy of individual blocks of the multiblock dataset.
    # Attributes are mapped by block pointers (vtkDataObject*), so these can
    # be queried by their flat index through a convenience function in the
    # attribute class (vtkCompositeDataDisplayAttributes::DataObjectFromIndex).
    # Alternatively, one can set attributes directly through the mapper using
    # flat indices.
    cdsa = vtkCompositeDataDisplayAttributes()
    mapper = vtkCompositePolyDataMapper(composite_data_display_attributes=cdsa)
    mbds >> mapper

    # This sets the block at flat index 3 red
    # Note that the index is the flat index in the tree, so the whole multiblock
    # is index 0 and the blocks are flat indexes 1, 2 and 3.  This affects
    # the block returned by mbds.GetBlock(2).
    mapper.SetBlockColor(3, colors.GetColor3d('Red'))
    # Color the spheres.
    mapper.SetBlockColor(1, colors.GetColor3d('LavenderBlush'))
    mapper.SetBlockColor(2, colors.GetColor3d('Lavender'))

    actor = vtkActor()
    actor.SetMapper(mapper)

    # Create the Renderer, RenderWindow, and RenderWindowInteractor.
    renderer = vtkRenderer(background=colors.GetColor3d('SteelBlue'))
    render_window = vtkRenderWindow(window_name='CompositePolyDataMapper')
    render_window.AddRenderer(renderer)
    render_window_interactor = vtkRenderWindowInteractor()
    render_window_interactor.render_window = render_window

    # Enable user interface interactor.
    renderer.AddActor(actor)
    render_window.Render()
    render_window_interactor.Start()


if __name__ == '__main__':
    main()
