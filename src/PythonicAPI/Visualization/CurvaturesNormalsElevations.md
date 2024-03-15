### Description

In this example we are coloring the surface by partitioning the Gaussian and Mean curvatures into bands with arrows colored by elevation to display the normals.

Rather beautiful surfaces are generated.

- [Gaussian Curvature](https://en.wikipedia.org/wiki/Gaussian_curvature), also [Wolfram MathWorld](https://mathworld.wolfram.com/GaussianCurvature.html)
- [Mean Curvature](https://en.wikipedia.org/wiki/Mean_curvature), also [Wolfram MathWorld](https://mathworld.wolfram.com/MeanCurvature.html)

The banded contour filter and an indexed/categorical lookup table is used to generate the curvature bands on the surface. To further enhance the surface, the surface normals are glyphed and colored by elevation using an ordinal lookup table.

Note that:

- If the regions on a surface have zero Gaussian curvature, then they can be flattened into a plane with no distortion, and the geometry of the region is Euclidean geometry.

- If the regions on a surface have positive Gaussian curvature, then the geometry of the surface is spherical geometry.

- If the regions on the surface have a negative Gaussian curvature, then the geometry of the surface is hyperbolic geometry.

In the above image you can see that the random hills incorporate all of these geometries.

The surface selected is the parametric random hills surface. The problem with the random hills surface is:

- Most of the gaussian curvatures will lie in the range -1 to 0.2 (say) with a few large values say 20 to 40 at the peaks of the hills.
- The edges of the random hills surface also have large irregular values so we need to handle these also. In order to fix this, a function is provided to adjust the edges.

So we need to manually generate custom bands to group the curvatures. The bands selected in the examples show that the surface is mostly planar with some hyperbolic regions (saddle points) and some spherical regions.

Feel free to experiment with different color schemes and/or the other sources from the parametric function group or the torus etc.

A histogram of the frequencies can be output to the console. This is useful if you want to get an idea of the distribution of the scalars in each band.
