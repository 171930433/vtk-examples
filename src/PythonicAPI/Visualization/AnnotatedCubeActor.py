#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkRenderingAnnotation import vtkAnnotatedCubeActor
from vtkmodules.vtkRenderingCore import (
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()

    # Set up the renderer, window, and interactor.
    #
    ren = vtkRenderer(background=colors.GetColor3d('Wheat'))
    ren_win = vtkRenderWindow(size=(640, 480), window_name='AnnotatedCubeActor')
    ren_win.AddRenderer(ren)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    # Set up the annotated cube.
    # We will use anatomic labelling.
    cube = vtkAnnotatedCubeActor(face_text_scale=2.0 / 3.0,
                                 x_plus_face_text='A', x_minus_face_text='P',
                                 y_plus_face_text='L', y_minus_face_text='R',
                                 z_plus_face_text='S', z_minus_face_text='I'
                                 )

    # Change the vector text colors.
    cube.text_edges_property.color = colors.GetColor3d('Black')
    cube.text_edges_property.line_width = 4

    cube.x_plus_face_property.color = colors.GetColor3d('Turquoise')
    cube.x_minus_face_property.color = colors.GetColor3d('Turquoise')
    cube.y_plus_face_property.color = colors.GetColor3d('Mint')
    cube.y_minus_face_property.color = colors.GetColor3d('Mint')
    cube.z_plus_face_property.color = colors.GetColor3d('Tomato')
    cube.z_minus_face_property.color = colors.GetColor3d('Tomato')

    ren.AddActor(cube)

    # Set up an interesting view.
    camera = ren.active_camera
    camera.view_up = (0, 0, 1)
    camera.focal_point = (0, 0, 0)
    camera.position = (4.5, 4.5, 2.5)
    ren.ResetCamera()
    camera.Dolly(1.0)
    ren.ResetCameraClippingRange()

    ren_win.Render()
    iren.Start()


if __name__ == '__main__':
    main()
