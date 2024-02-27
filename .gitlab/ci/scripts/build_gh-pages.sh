#!/bin/sh
source venv/vtk-examples-web/bin/activate
python -m pip install --upgrade pip
pip install wheel
pip install mkdocs-material htmlmin
git clone git@github.com:Kitware/vtk-examples.git /pages
pushd /pages
git checkout gh-pages
popd
OLDHOME=${HOME}
HOME=${PWD}
src/SyncSiteWithRepo.sh https://gitlab.kitware.com/vtk/vtk-examples https://examples.vtk.org/site/ https://github.com/Kitware/vtk-examples /pages vtk_build/vtk
HOME=${OLDHOME}
pushd /pages
git add .
git commit -m "nightly update"
git push
