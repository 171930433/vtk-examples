#!/bin/bash
exclude_dirs=(Deprecated Untested Databases Developers Snippets Qt)
shopt -s extglob
mkdir build_examples
mkdir pregen_examples
for topic in src/Cxx/*/; do
    topic_name=$(basename ${topic})
    if [[ ! $(echo ${exclude_dirs[@]} | grep -Fw ${topic_name}) ]]; then
        for f in ${topic}/*.cxx; do
            name=$(basename ${f} .cxx)
            if ! grep -Fxq "$name" src/Admin/WASM/exclude_wasm.txt; then
                echo ${name}
                target_path=pregen_examples/${topic_name}/${name}
                mkdir -p ${target_path}
                cp ${f} ${target_path}
                for addon_file in ${topic}/${name}.!(md); do
                    cp ${addon_file} ${target_path}
                done
                python3 .gitlab/GenerateHtmlCMake.py ${f} ${target_path} vtk
            fi
        done
    fi
done
python3 .gitlab/GenerateSuperCMake.py
emcmake cmake -GNinja \
    -DEMSCRIPTEN:Bool=true \
    -DVTK_DIR=$CI_PROJECT_DIR/vtk/build \
    -DDEBUGINFO=NONE \
    -DOPTIMIZE=SMALLEST \
    -S pregen_examples -B build_examples
cmake --build build_examples
