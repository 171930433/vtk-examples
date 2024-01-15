import json
import shutil
import glob
import os
import errno

with open('src/Admin/WASM/packaged_files.json') as f:
    data = json.load(f)

for package_attr, package_val in data.items():
    os.makedirs('packages_fs/' + package_attr)
    for filename_attr, filename_val in package_val.items():
        if filename_val['type'] == 'dir':
            os.makedirs('packages_fs/' + package_attr + '/' + filename_attr)
            for target in filename_val['path']:
                for globtarget in glob.glob('src/Testing/Data/' + target):
                    try:
                        shutil.copytree(globtarget, 'packages_fs/' + package_attr + '/' + filename_attr + '/' + os.path.basename(globtarget))
                    except OSError as exc: # copy file or directory
                        if exc.errno in (errno.ENOTDIR, errno.EINVAL):
                            shutil.copy(globtarget, 'packages_fs/' + package_attr + '/' + filename_attr)
                        elif exc.errno == errno.EEXIST:
                            pass
                        else: raise
        else:
            shutil.copy('src/Testing/Data/' + filename_val['path'][0], 'packages_fs/' + package_attr + '/' + filename_attr)
