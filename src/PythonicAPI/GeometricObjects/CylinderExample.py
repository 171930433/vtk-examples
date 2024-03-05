#!/usr/bin/env python3

# This simple example shows how to do basic rendering and pipeline creation.

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersSources import vtkCylinderSource
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()
    # Set the background color.
    bkg = map(lambda x: x / 255.0, [26, 51, 102, 255])
    colors.SetColor('BkgColor', *bkg)

    # This creates a polygonal cylinder model with eight circumferential facets.
    # We can initialize the properties of a wrapped VTK class by specifying keyword arguments in the constructor.
    cylinder = vtkCylinderSource(resolution=8)
    # We can also print the properties of a VTK object in a more pythonic way.
    print(
        f'Cylinder properties:\n   height: {cylinder.height}, radius: {cylinder.radius},'
        f' center: {cylinder.center} resolution: {cylinder.resolution} capping: {cylinder.capping == 1}')

    # We can do this by directly mapping the input connection to the output port.
    # cm = vtkPolyDataMapper(input_connection=cylinder.output_port)
    # Or make a pipeline ...
    cm = vtkPolyDataMapper()
    ca = vtkActor(mapper=cm)
    # Our pipeline, linking the source to the mapper.
    cylinder >> cm

    ca.RotateX(30)
    ca.RotateY(-45)
    ca.property.color = colors.GetColor3d('Tomato')

    # Note the setting of the background by calling GetColor3D()
    ren = vtkRenderer(background=colors.GetColor3d('BkgColor'))
    ren.AddActor(ca)

    ren_win = vtkRenderWindow(size=[300, 300], window_name='CylinderExample')
    ren_win.AddRenderer(ren)

    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    iren.Initialize()
    ren.ResetCamera()
    ren.active_camera.Zoom(1.5)
    ren_win.Render()

    # Start the event loop.
    iren.Start()


if __name__ == '__main__':
    main()
