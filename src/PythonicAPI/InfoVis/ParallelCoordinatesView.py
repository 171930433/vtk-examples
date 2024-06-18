#!/usr/bin/env python3

# Example of how to use Parallel Coordinates View to plot and compare
# data set attributes.
# Use the 'u' character to toggle between 'inspect modes' on the parallel
# coordinates view (i.e. between selecting data and manipulating axes).
# Lines which are commented out show alternative options.

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersCore import vtkElevationFilter
from vtkmodules.vtkFiltersGeneral import vtkBrownianPoints
from vtkmodules.vtkImagingCore import vtkRTAnalyticSource
from vtkmodules.vtkImagingGeneral import vtkImageGradient
from vtkmodules.vtkViewsInfovis import (
    vtkParallelCoordinatesRepresentation,
    vtkParallelCoordinatesView
)


def main():
    colors = vtkNamedColors()

    # Generate an example image data set with multiple attribute arrays to probe
    # and view.
    # This is where you would put your reader instead of this rt->elev pipeline...
    rt = vtkRTAnalyticSource(whole_extent=(-3, 3, -3, 3, -3, 3))
    grad = vtkImageGradient(dimensionality=3)
    brown = vtkBrownianPoints(minimum_speed=0.5, maximum_speed=1.0)
    elev = vtkElevationFilter(low_point=(-3, -3, -3), high_point=(3, 3, 3))

    # Set up the parallel coordinates Representation to be used in the View.
    # Set use_curves=1 to use smooth curves.
    rep = vtkParallelCoordinatesRepresentation(use_curves=0, line_opacity=0.5,
                                               axis_color=colors.GetColor3d('Gold'),
                                               line_color=colors.GetColor3d('MistyRose'))

    # List all the attribute arrays you want plotted in parallel coordinates.
    rep.SetInputArrayToProcess(0, 0, 0, 0, 'RTDataGradient')
    rep.SetInputArrayToProcess(1, 0, 0, 0, 'RTData')
    rep.SetInputArrayToProcess(2, 0, 0, 0, 'Elevation')
    rep.SetInputArrayToProcess(3, 0, 0, 0, 'BrownianVectors')

    # Plug your reader in here for your own data.
    rt >> grad >> brown >> elev >> rep

    # Set up the Parallel Coordinates View and hook in the Representation.
    view = vtkParallelCoordinatesView()
    view.SetRepresentation(rep)

    # Inspect Mode determines whether your interactions manipulate the axes or select data.
    # view.SetInspectMode(view.VTK_INSPECT_MANIPULATE_AXES)    # VTK_INSPECT_MANIPULATE_AXES = 0,
    view.SetInspectMode(view.VTK_INSPECT_SELECT_DATA)  # VTK_INSPECT_SELECT_DATA = 1

    # Brush Mode determines the type of interaction you perform to select data.
    view.SetBrushModeToLasso()
    # view.SetBrushModeToAngle()
    # view.SetBrushModeToFunction()
    # view.SetBrushModeToAxisThreshold()  # not implemented yet (as of 21 Feb 2010)

    # Brush Operator determines how each new selection interaction changes.
    # selected lines
    # view.SetBrushOperatorToAdd()
    # view.SetBrushOperatorToSubtract()
    # view.SetBrushOperatorToIntersect()
    view.SetBrushOperatorToReplace()

    def toggle_inspectors(obj, event):
        # Define the callback routine which toggles between 'Inspect Modes'.
        if view.inspect_mode == 0:
            view.inspect_mode = 1
        else:
            view.inspect_mode = 0

    # Hook up the callback to toggle between inspect modes
    # (manip axes & select data).
    view.interactor.AddObserver('UserEvent', toggle_inspectors)

    # Set up the render window.
    view.render_window.size = (600, 300)
    view.render_window.WindowName = 'ParallelCoordinatesView'
    view.renderer.gradient_background = True
    view.renderer.background2 = colors.GetColor3d('DarkBlue')
    view.renderer.background = colors.GetColor3d('MidnightBlue')
    view.ResetCamera()
    view.Render()

    # Start interaction event loop.
    view.interactor.Start()


if __name__ == '__main__':
    main()
