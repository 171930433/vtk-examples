#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import vtkPolyData
from vtkmodules.vtkFiltersSources import (
    vtkPointSource,
    vtkSphereSource
)
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkGlyph3DMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()

    # create a rendering window and renderer
    ren = vtkRenderer(background=colors.GetColor3d('RoyalBLue'))
    ren_win = vtkRenderWindow()
    ren_win.AddRenderer(ren)
    ren_win.SetWindowName('InteractorStyleTrackballCamera')

    # Create a render window interactor.
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    style = vtkInteractorStyleTrackballCamera()
    iren.interactor_style = style

    # Create the source, mapper and actor.
    src = vtkPointSource(center=(0, 0, 0), number_of_points=50, radius=5)

    actor = point_to_glyph(src.update().output.points, 0.05)
    actor.GetProperty().SetColor(colors.GetColor3d('Gold'))

    ren.AddActor(actor)

    # Enable the user interface interactor.
    iren.Initialize()
    ren_win.Render()
    iren.Start()


def point_to_glyph(points, scale):
    """
    Convert points to glyphs.
    :param points: The points to glyph.
    :param scale: The scale, used to determine the size of the
                  glyph representing the point, expressed as a
                  fraction of the largest side of the bounding
                  box surrounding the points. e.g. 0.05
    :return: The actor.
    """

    bounds = points.bounds
    max_len = 0.0
    for i in range(0, 3):
        max_len = max(bounds[i + 1] - bounds[i], max_len)

    sphere_source = vtkSphereSource(radius=scale * max_len)
    # sphere_source.SetRadius(scale * max_len)

    pd = vtkPolyData(points=points)
    # pd.SetPoints(points)

    mapper = vtkGlyph3DMapper(source_data=sphere_source.update().output, scalar_visibility=False, scaling=False)
    pd >> mapper

    return vtkActor(mapper=mapper)


if __name__ == '__main__':
    main()
