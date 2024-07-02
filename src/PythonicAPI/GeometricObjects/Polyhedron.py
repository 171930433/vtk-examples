#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import (
    vtkIdList,
    vtkPoints
)
from vtkmodules.vtkCommonDataModel import (
    VTK_POLYHEDRON,
    vtkUnstructuredGrid
)
from vtkmodules.vtkIOXML import vtkXMLUnstructuredGridWriter
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()

    # Create a polyhedron (cube).
    # The point Ids are: (0, 1, 2, 3, 4, 5, 6, 7)

    points = vtkPoints()
    points.InsertNextPoint(-1.0, -1.0, -1.0)
    points.InsertNextPoint(1.0, -1.0, -1.0)
    points.InsertNextPoint(1.0, 1.0, -1.0)
    points.InsertNextPoint(-1.0, 1.0, -1.0)
    points.InsertNextPoint(-1.0, -1.0, 1.0)
    points.InsertNextPoint(1.0, -1.0, 1.0)
    points.InsertNextPoint(1.0, 1.0, 1.0)
    points.InsertNextPoint(-1.0, 1.0, 1.0)

    # These are the point ids corresponding to each face.
    faces = [[0, 3, 2, 1], [0, 4, 7, 3], [4, 5, 6, 7], [5, 1, 2, 6], [0, 1, 5, 4], [2, 3, 7, 6]]
    face_id = vtkIdList()
    face_id.InsertNextId(6)  # Six faces make up the cell.
    for face in faces:
        face_id.InsertNextId(len(face))  # The number of points in the face.
        [face_id.InsertNextId(i) for i in face]

    ugrid = vtkUnstructuredGrid(points=points)
    ugrid.InsertNextCell(VTK_POLYHEDRON, face_id)

    # Here we write out the cube.
    writer = vtkXMLUnstructuredGridWriter(input_data=ugrid, file_name='polyhedron.vtu',
                                          data_mode=vtkXMLUnstructuredGridWriter.Ascii)
    writer.update()

    # Create a mapper and actor.
    mapper = vtkDataSetMapper()
    ugrid >> mapper

    actor = vtkActor(mapper=mapper)
    actor.property.color = colors.GetColor3d('Silver')

    # Visualize
    ren = vtkRenderer(background=colors.GetColor3d('Salmon'))
    ren_win = vtkRenderWindow(window_name='Polyhedron')
    ren_win.AddRenderer(ren)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    ren.AddActor(actor)
    ren.ResetCamera()
    ren.active_camera.Azimuth(30)
    ren.active_camera.Elevation(30)
    ren_win.Render()
    iren.Start()


if __name__ == '__main__':
    main()
