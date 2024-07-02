#!/usr/bin/env python3

"""
Modified from VTK/Examples/GUI/Python/StreamlinesWithLineWidget.py.
This program encompasses the functionality of
  StreamlinesWithLineWidget.tcl and LineWidget.tcl.
"""

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import vtkPolyData
from vtkmodules.vtkCommonMath import vtkRungeKutta4
from vtkmodules.vtkFiltersCore import vtkStructuredGridOutlineFilter
from vtkmodules.vtkFiltersFlowPaths import vtkStreamTracer
from vtkmodules.vtkFiltersModeling import vtkRibbonFilter
from vtkmodules.vtkIOParallel import vtkMultiBlockPLOT3DReader
from vtkmodules.vtkInteractionWidgets import vtkLineWidget
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()

    xyz_fn, q_fn, num_of_stream_lines, illustration = get_program_parameters()
    if illustration:
        num_of_stream_lines = 25

    # Start by loading some data.
    # scalar_function_number=100 is density and vector_function_number=202 is momentum.
    pl3d = vtkMultiBlockPLOT3DReader(xyz_file_name=xyz_fn, q_file_name=q_fn,
                                     scalar_function_number=100, vector_function_number=202)
    pl3d_output = pl3d.update().output.GetBlock(0)

    # Create the Renderer, RenderWindow and RenderWindowInteractor.
    ren = vtkRenderer(background=colors.GetColor3d('Silver'))
    ren_win = vtkRenderWindow(size=(512, 512), window_name='StreamlinesWithLineWidget')
    ren_win.AddRenderer(ren)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    # Needed by: vtkStreamTracer and vtkLineWidget.
    seeds = vtkPolyData()
    seeds2 = vtkPolyData()

    # The line widget is used seed the streamlines.
    line_widget = vtkLineWidget(resolution=num_of_stream_lines, input_data=pl3d_output)
    line_widget.poly_data = seeds
    if illustration:
        line_widget.SetAlignToNone()
        line_widget.point1 = (0.974678, 5.073630, 31.217961)
        line_widget.point2 = (0.457544, -4.995921, 31.080175)
    else:
        line_widget.SetAlignToYAxis()
    line_widget.clamp_to_bounds = True
    line_widget.PlaceWidget()

    # The second line widget is used seed more streamlines.
    line_widget2 = vtkLineWidget(resolution=num_of_stream_lines, input_data=pl3d_output)
    line_widget2.poly_data = seeds2
    line_widget2.SetKeyPressActivationValue('L')
    line_widget2.SetAlignToZAxis()
    line_widget.clamp_to_bounds = True
    line_widget2.PlaceWidget()

    # Here we set up two streamlines.
    rk4 = vtkRungeKutta4()
    streamer = vtkStreamTracer(integrator=rk4, input_data=pl3d_output, source_data=seeds,
                               maximum_propagation=100, initial_integration_step=0.2, compute_vorticity=True)
    streamer.SetIntegrationDirectionToForward()

    rf = vtkRibbonFilter(width=0.1, width_factor=5)
    stream_mapper = vtkPolyDataMapper(scalar_range=pl3d_output.scalar_range)
    streamer >> rf >> stream_mapper
    streamline = vtkActor(mapper=stream_mapper, visibility=False)

    streamer2 = vtkStreamTracer(integrator=rk4, input_data=pl3d_output, source_data=seeds2,
                                maximum_propagation=100, initial_integration_step=0.2, compute_vorticity=True)

    rf2 = vtkRibbonFilter(width=0.1, width_factor=5)
    stream_mapper2 = vtkPolyDataMapper(scalar_range=pl3d_output.scalar_range)
    streamer2 >> rf2 >> stream_mapper2
    streamline2 = vtkActor(mapper=stream_mapper2, visibility=False)

    # Get an outline of the data set for context.
    outline = vtkStructuredGridOutlineFilter()
    outline_mapper = vtkPolyDataMapper()
    pl3d_output >> outline >> outline_mapper
    outline_actor = vtkActor(mapper=outline_mapper)
    outline_actor.property.color = colors.GetColor3d('Black')

    # Add the actors to the renderer, set the background and size.
    ren.AddActor(outline_actor)
    ren.AddActor(streamline)
    ren.AddActor(streamline2)

    # Associate the line widgets with the interactor and setup callbacks.
    line_widget.SetInteractor(iren)
    line_widget.AddObserver('StartInteractionEvent', EnableActorCallback(streamline))
    line_widget.AddObserver('InteractionEvent', GenerateStreamlinesCallback(seeds, ren_win))
    line_widget2.SetInteractor(iren)
    line_widget2.AddObserver('StartInteractionEvent', EnableActorCallback(streamline2))
    line_widget2.AddObserver('InteractionEvent', GenerateStreamlinesCallback(seeds2, ren_win))

    cam = ren.active_camera
    if illustration:
        # We need to directly display the streamlines in this case.
        line_widget.EnabledOn()
        streamline.VisibilityOn()
        line_widget.GetPolyData(seeds)
        ren_win.Render()

        cam.clipping_range = (14.216207, 68.382915)
        cam.focal_point = (9.718210, 0.458166, 29.399900)
        cam.position = (-15.827551, -16.997463, 54.003120)
        cam.view_up = (0.616076, 0.179428, 0.766979)
    else:
        cam.clipping_range = (3.95297, 50)
        cam.focal_point = (9.71821, 0.458166, 29.3999)
        cam.position = (2.7439, -37.3196, 38.7167)
        cam.view_up = (-0.16123, 0.264271, 0.950876)

    iren.Initialize()
    ren_win.Render()
    iren.Start()


def get_program_parameters():
    import argparse
    description = 'Produce streamlines in the combustor dataset.'
    epilogue = '''
        Produce streamlines in the combustor dataset.

This example demonstrates how to use the vtkLineWidget to seed and
manipulate streamlines. Two line widgets are created. The first is invoked
by pressing 'i', the second by pressing 'L' (capital). Both can exist
together.

By default, the illustration is selected, in this case:
 1) The number of streamlines is set to 25.
 2) The camera position and first line widget are positioned differently.
 3) The streamlines are displayed running from the first line widget.
 4) The second line widget is still available.

   '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('xyz_fn', help='combxyz.bin.')
    parser.add_argument('q_fn', help='combq.bin.')
    parser.add_argument('-s', '--stream_lines', default=25, type=int, help='The number of stream lines.')
    parser.add_argument('-n', '--no_illustration', action='store_false',
                        help='Reproduce Fig 7-39 of the VTK Textbook by default.')
    args = parser.parse_args()
    return args.xyz_fn, args.q_fn, args.stream_lines, args.no_illustration


class EnableActorCallback(object):
    def __init__(self, actor):
        self.actor = actor

    def __call__(self, caller, ev):
        self.actor.visibility = True


class GenerateStreamlinesCallback(object):
    def __init__(self, poly_data, ren_win):
        self.poly_data = poly_data
        self.ren_win = ren_win

    def __call__(self, caller, ev):
        caller.GetPolyData(self.poly_data)
        self.ren_win.Render()


if __name__ == '__main__':
    main()
