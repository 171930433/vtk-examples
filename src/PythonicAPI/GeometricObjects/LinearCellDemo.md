### Description

Linear cell types found in VTK.

The numbers define ordering of the defining points. As a general guide, for non-planar three-dimensional objects, the back face indices in the views are numbered 0, 1, 2, however, for the VTK_WEDGE, the back face is 0, 4, 3. Of course, if you change the orientation, you will get different numbering for the back face.

Options are provided to show a wire frame (`-w`) or to add a back face color (`-b`).

With the back face option selected, the back face color will be visible as the objects are semitransparent.
