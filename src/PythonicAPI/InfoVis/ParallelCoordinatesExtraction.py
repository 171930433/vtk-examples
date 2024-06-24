#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkLookupTable
from vtkmodules.vtkFiltersCore import vtkElevationFilter
from vtkmodules.vtkFiltersExtraction import vtkExtractSelection
from vtkmodules.vtkFiltersGeneral import (
    vtkAnnotationLink,
    vtkBrownianPoints
)
from vtkmodules.vtkFiltersModeling import vtkOutlineFilter
from vtkmodules.vtkImagingCore import vtkRTAnalyticSource
from vtkmodules.vtkImagingGeneral import vtkImageGradient
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)
from vtkmodules.vtkViewsInfovis import (
    vtkParallelCoordinatesRepresentation,
    vtkParallelCoordinatesView
)


# Example of how to use Parallel Coordinates View to plot and compare
# data set attributes, and then to use selections in the parallel coordinates
# view to extract and view data points associated with those selections.
# Use the 'u' character to toggle between 'inspect modes' on the parallel
# coordinates view (i.e. between selecting data and manipulating axes).
# Note that no points will show up inside the 3d box outline until you
# select some lines/curves in the parallel coordinates view.


def main():
    colors = vtkNamedColors()

    # Generate an image data set with multiple attribute arrays to probe and view.
    rt = vtkRTAnalyticSource(whole_extent=(-3, 3, -3, 3, -3, 3))
    grad = vtkImageGradient(dimensionality=3)
    brown = vtkBrownianPoints(minimum_speed=0.5, maximum_speed=1.0)
    elev = vtkElevationFilter(low_point=(-3, -3, -3), high_point=(3, 3, 3))

    # Updating here because I will need to probe scalar ranges before
    # the render window updates the pipeline.
    (rt >> grad >> brown >> elev).update()

    # Set up parallel coordinates representation to be used in View.
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
    elev >> rep

    # Set up the Parallel Coordinates View and hook in representation.
    view = vtkParallelCoordinatesView()
    view.SetRepresentation(rep)
    view.SetInspectMode(view.VTK_INSPECT_SELECT_DATA)
    view.SetBrushOperatorToReplace()
    view.SetBrushModeToLasso()

    # Create a annotation link to access selection in parallel coordinates view
    annotation_link = vtkAnnotationLink()
    # If you don't set the FieldType explicitly it ends up as UNKNOWN
    # (as of 21 Feb 2010)
    # See vtkSelectionNode doc for field and content type enum values
    annotation_link.GetCurrentSelection().GetNode(0).SetFieldType(1)  # Point
    annotation_link.GetCurrentSelection().GetNode(0).SetContentType(4)  # Indices
    # Update before passing annotation_link to vtkExtractSelection
    annotation_link.update()
    # Connect the annotation link to the parallel coordinates representation
    rep.annotation_link = annotation_link

    # Extract the portion of data corresponding to the parallel coordinates selection
    extract = vtkExtractSelection()
    extract.SetInputConnection(0, elev.output_port)
    extract.SetInputConnection(1, annotation_link.GetOutputPort(2))

    def update_render_windows(obj, event):
        """
        Handle updating of RenderWindow since it's not a 'View'
        and so not covered by vtkViewUpdater

        :param obj:
        :param event:
        :return:
        """
        # ren.ResetCamera()
        # ren_win.Render()
        ren_win.GetRenderWindow()

    # Set up callback to update 3D render window when selections are changed in
    # parallel coordinates view.
    annotation_link.AddObserver('AnnotationChangedEvent', update_render_windows)

    def toggle_inspectors(obj, event):
        # Define the callback routine which toggles between 'Inspect Modes'.
        if view.inspect_mode == 0:
            view.inspect_mode = 1
        else:
            view.inspect_mode = 0

    # Set up callback to toggle between inspect modes (manip axes & select data)
    view.interactor.AddObserver('UserEvent', toggle_inspectors)

    # 3D outline of image data bounds
    outline = vtkOutlineFilter()
    outline_mapper = vtkPolyDataMapper()
    elev >> outline >> outline_mapper
    outline_actor = vtkActor(mapper=outline_mapper)

    # Build the lookup table for the 3d data scalar colors (brown to white)
    lut = vtkLookupTable(table_range=(0, 256),
                         hue_range=(0.1, 0.1), saturation_range=(1.0, 0.1), value_range=(0.4, 1.0))

    # Set up the 3d rendering parameters of the
    # image data which is selected in parallel coordinates.
    coloring_by = 'Elevation'
    data = elev.GetOutputDataObject(0).GetPointData()
    data_mapper = vtkDataSetMapper(scalar_mode=Mapper.ScalarMode.VTK_SCALAR_MODE_USE_POINT_FIELD_DATA,
                                   color_mode=Mapper.ColorMode.VTK_COLOR_MODE_MAP_SCALARS,
                                   scalar_visibility=True,
                                   scalar_range=data.GetArray(coloring_by).range,
                                   lookup_table=lut)
    extract >> data_mapper
    data_actor = vtkActor(mapper=data_mapper)
    data_actor.property.representation = Property.Representation.VTK_POINTS
    data_actor.property.point_size = 10

    # Finalize parallel coordinates view.
    view.render_window.size = (600, 300)
    view.render_window.WindowName = 'ParallelCoordinatesExtraction'
    view.renderer.gradient_background = True
    view.renderer.background2 = colors.GetColor3d('DarkBlue')
    view.renderer.background = colors.GetColor3d('MidnightBlue')

    # Set up the 3d render window and add both actors
    ren = vtkRenderer()
    # ren = view.renderer
    ren_win = vtkRenderWindow()
    # ren_win = view.render_window
    ren_win.AddRenderer(ren)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    ren.AddActor(outline_actor)
    ren.AddActor(data_actor)

    ren.ResetCamera()
    ren_win.Render()

    # Set up the render window.
    view.ResetCamera()
    view.Render()

    view.interactor.Start()


@dataclass(frozen=True)
class Mapper:
    @dataclass(frozen=True)
    class ColorMode:
        VTK_COLOR_MODE_DEFAULT: int = 0
        VTK_COLOR_MODE_MAP_SCALARS: int = 1
        VTK_COLOR_MODE_DIRECT_SCALARS: int = 2

    @dataclass(frozen=True)
    class ResolveCoincidentTopology:
        VTK_RESOLVE_OFF: int = 0
        VTK_RESOLVE_POLYGON_OFFSET: int = 1
        VTK_RESOLVE_SHIFT_ZBUFFER: int = 2

    @dataclass(frozen=True)
    class ScalarMode:
        VTK_SCALAR_MODE_DEFAULT: int = 0
        VTK_SCALAR_MODE_USE_POINT_DATA: int = 1
        VTK_SCALAR_MODE_USE_CELL_DATA: int = 2
        VTK_SCALAR_MODE_USE_POINT_FIELD_DATA: int = 3
        VTK_SCALAR_MODE_USE_CELL_FIELD_DATA: int = 4
        VTK_SCALAR_MODE_USE_FIELD_DATA: int = 5


@dataclass(frozen=True)
class Property:
    @dataclass(frozen=True)
    class Interpolation:
        VTK_FLAT: int = 0
        VTK_GOURAUD: int = 1
        VTK_PHONG: int = 2
        VTK_PBR: int = 3

    @dataclass(frozen=True)
    class Representation:
        VTK_POINTS: int = 0
        VTK_WIREFRAME: int = 1
        VTK_SURFACE: int = 2


if __name__ == '__main__':
    main()
