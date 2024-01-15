import shutil
import glob

shutil.copyfile('.gitlab/templates/CMakeLists_global.txt.template', 'pregen_examples/CMakeLists.txt')
with open('pregen_examples/CMakeLists.txt', 'r') as cmake:
    data = cmake.read()

subdirectories = []
for path in glob.glob('pregen_examples/**/CMakeLists.txt', recursive=True):
    if path != 'pregen_examples/CMakeLists.txt':
        subdirectories.append('add_subdirectory(' + path.removeprefix('pregen_examples/').removesuffix('CMakeLists.txt') + ')')
data = data.replace('XXX', '\n'.join(subdirectories))

with open('pregen_examples/CMakeLists.txt', 'w') as cmake:
    cmake.write(data)
