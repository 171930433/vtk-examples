#!/bin/bash
for file in packaged_data/*; do
    gzip ${file}
    mv ${file}.gz ${file}
done
rsync -av packaged_data/ kitware@web.kitware.com:/data/
