#!/bin/bash

git clone --depth 1 --branch 3.1.60 https://github.com/emscripten-core/emsdk.git
cd emsdk
./emsdk install 3.1.60
./emsdk activate 3.1.60
./upstream/emscripten/embuilder.py build sdl2
