#!/bin/bash
if [ ! -d vtk_build ]; then
    mkdir vtk_build
    cd vtk_build
    git clone https://gitlab.kitware.com/vtk/vtk.git
    mkdir build
    emcmake cmake \
        -GNinja -DBUILD_SHARED_LIBS:BOOL=OFF \
        -DCMAKE_BUILD_TYPE:STRING=Release \
        -DVTK_ENABLE_LOGGING:BOOL=OFF \
        -DVTK_ENABLE_WRAPPING:BOOL=OFF \
        -DVTK_MODULE_ENABLE_VTK_cli11:STRING=YES \
        -DVTK_MODULE_ENABLE_VTK_RenderingLICOpenGL2:STRING=DONT_WANT \
        -DVTK_BUILD_TESTING=ON \
        -S vtk  -B build
    mkdir install
else
    cd vtk_build/vtk
    git pull
    cd ..
fi
cmake --build build
cmake --install build --prefix $CI_PROJECT_DIR/vtk_build/install
