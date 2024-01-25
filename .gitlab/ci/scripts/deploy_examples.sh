#!/bin/bash
shopt -s extglob
for topic in build_examples/!(CMakeFiles)/; do
    for example in ${topic}/*/; do
        mkdir ${example}/upload
        example_name=$(basename ${example})
        gzip ${example}/${example_name}.wasm
        mv ${example}/${example_name}.wasm.gz ${example}/upload/${example_name}.wasm
        gzip ${example}/${example_name}.js
        mv ${example}/${example_name}.js.gz ${example}/upload/${example_name}.js
        gzip ${example}/index.html
        mv ${example}/index.html.gz ${example}/upload/index.html
        rsync -r ${example}/upload/ kitware@web.kitware.com:/${example_name}/
    done
done
