#!/bin/bash
if [ ! -d vtk ]; then
    git clone https://gitlab.kitware.com/vtk/vtk.git
    cd vtk
    mkdir build
    emcmake cmake \
        -GNinja -DBUILD_SHARED_LIBS:BOOL=OFF \
        -DCMAKE_BUILD_TYPE:STRING=Release \
        -DVTK_ENABLE_LOGGING:BOOL=OFF \
        -DVTK_ENABLE_WRAPPING:BOOL=OFF \
        -DVTK_MODULE_ENABLE_VTK_cli11:STRING=YES \
        -DVTK_MODULE_ENABLE_VTK_RenderingLICOpenGL2:STRING=DONT_WANT \
        -DVTK_BUILD_TESTING=ON \
        -S . -B build
else
    cd vtk
    git pull
fi
cmake --build build
