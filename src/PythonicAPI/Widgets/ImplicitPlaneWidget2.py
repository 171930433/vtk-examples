#!/usr/bin/env python3

from pathlib import Path

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingUI
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkCommand
from vtkmodules.vtkCommonDataModel import vtkPlane
from vtkmodules.vtkFiltersCore import (
    vtkClipPolyData
)
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkIOXML import vtkXMLPolyDataReader
from vtkmodules.vtkInteractionWidgets import (
    vtkImplicitPlaneRepresentation,
    vtkImplicitPlaneWidget2
)
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkProperty,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main(fn):
    colors = vtkNamedColors()
    sphere_source = vtkSphereSource(radius=10.0)

    fp = None
    if fn:
        fp = Path(fn)
        if not (fp.is_file() and fp.suffix == '.vtp'):
            print(f'Expected an existing file name with extension .vtp\n  got: {fp}')
            return

    # Setup a visualization pipeline.
    plane = vtkPlane()
    clipper = vtkClipPolyData(clip_function=plane, inside_out=True)
    if fp:
        reader = vtkXMLPolyDataReader(file_name=fp)
        reader >> clipper
    else:
        sphere_source >> clipper

    back_faces = vtkProperty(diffuse_color=colors.GetColor3d('Gold'))

    # Create a mapper and actor.
    mapper = vtkPolyDataMapper()
    clipper >> mapper
    actor = vtkActor(mapper=mapper, backface_property=back_faces)

    # A renderer and render window.
    renderer = vtkRenderer(background=colors.GetColor3d('SlateGray'))
    ren_win = vtkRenderWindow(window_name='ImplicitPlaneWidget2')
    ren_win.AddRenderer(renderer)

    renderer.AddActor(actor)

    # An interactor.
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    # The callback will do the work.
    my_callback = IPWCallback(plane)

    rep = vtkImplicitPlaneRepresentation()
    rep.place_factor = 1.25  # This must be set prior to placing the widget.
    rep.PlaceWidget(actor.bounds)
    rep.normal = plane.normal

    plane_widget = vtkImplicitPlaneWidget2(representation=rep, interactor=iren)
    plane_widget.AddObserver(vtkCommand.InteractionEvent, my_callback)

    renderer.active_camera.Azimuth(-60)
    renderer.active_camera.Elevation(30)
    renderer.ResetCamera()
    renderer.active_camera.Zoom(0.75)

    # Render and interact.
    iren.Initialize()
    ren_win.Render()
    plane_widget.On()

    # Begin mouse interaction.
    iren.Start()


class IPWCallback:
    def __init__(self, plane):
        self.plane = plane

    def __call__(self, caller, ev):
        rep = caller.representation
        rep.GetPlane(self.plane)


def get_program_parameters():
    import argparse
    description = 'How to use the second generation ImplicitPlaneWidget2 to interactively' \
                  ' define the clipping plane for a polydata.'
    epilogue = '''
    If no arguments are specified, a vtkSphereSource generates the polydata.
    By specifying a .vtp file, the example can operate on arbitrary polydata.
'''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('file_name', nargs='?', default=None, help='A VTK Poly Data file e.g. cow.vtp')

    args = parser.parse_args()
    return args.file_name


if __name__ == '__main__':
    file_name = get_program_parameters()
    main(file_name)
