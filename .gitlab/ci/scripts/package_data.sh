#!/bin/bash
for f in $(find src/SupplementaryData/Cxx -type f); do
    if [[ "$f" == *.zip ]]; then
        mkdir src/Testing/Data/$(basename $f .zip)
        unzip $f -d src/Testing/Data/$(basename $f .zip)
    else
        cp $f src/Testing/Data
    fi
done
mkdir packages_fs
python3 .gitlab/make_packages.py
mkdir packaged_data
for f in packages_fs/*; do
    filename=$(basename $f)
    /emsdk/upstream/emscripten/tools/file_packager packaged_data/${filename}.data --preload $f@/ --js-output=packaged_data/${filename}.js
done
