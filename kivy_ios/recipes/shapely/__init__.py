# pure-python package, this can be removed when we'll support any python package
import glob
import shutil
from os import listdir
from os.path import join

import sh

from kivy_ios.toolchain import CythonRecipe, shprint


class NewShapely2(CythonRecipe):
    version = "2.0.2"
    url = "https://github.com/shapely/shapely/archive/refs/tags/{version}.zip"
    library = "libshapely.a"
    depends = ["python", "geos-ios", "numpy"]

    def prebuild_platform(self, plat):
        if self.has_marker("patched"):
            return
        self.apply_patch("link.patch")

        python_recipe = self.get_recipe('python3', self.ctx)
        os_specific_numpy_def_dirs = glob.glob('{}/numpy/{}/numpy-*/build/src.macosx-*/numpy/core/include'.format(
            python_recipe.ctx.build_dir,
            plat.name,
        ))
        os_specific_numpy_defs = os_specific_numpy_def_dirs[0]
        python_include_numpy = join(self.ctx.dist_dir, "include", "common", 'numpy')
        shutil.copytree(python_include_numpy, join(self.build_dir, "numpy"))
        self.copy_files(join(os_specific_numpy_defs, "numpy"), join(self.build_dir, "numpy", "numpy"))
        self.set_marker("patched")
        print("patch applied")
        pass


    @staticmethod
    def copy_files(src, dest):
        files = listdir(src)
        for fname in files:
            shutil.copy2(join(src, fname), dest)

    def get_recipe_env(self, plat):
        env = super().get_recipe_env(plat)
        lib_root = join(self.ctx.dist_dir, "lib")
        geos_recipe = self.get_recipe('geos-ios', self.ctx)
        geos = glob.glob("{}/geos-ios/{}/geos-*/include".format(geos_recipe.ctx.build_dir, plat.name))
        print(geos)
        env['GEOS_INCLUDE_PATH'] = geos[0]
        env['GEOS_LIBRARY_PATH'] = lib_root
        env['PYTHONPATH'] = self.ctx.site_packages_dir
        python_include_numpy = join(self.build_dir, "numpy")

        arch_inc = join(self.ctx.dist_dir, "include", plat.name, "numpy")
        common_inc = join(self.ctx.dist_dir, "include", "common", "numpy")

        env['CFLAGS'] = env['CFLAGS'].replace(arch_inc, python_include_numpy)
        env['OTHER_CFLAGS'] = env['OTHER_CFLAGS'].replace(arch_inc, python_include_numpy)
        env['CFLAGS'] = env['CFLAGS'].replace(common_inc, python_include_numpy)
        env['OTHER_CFLAGS'] = env['OTHER_CFLAGS'].replace(common_inc, python_include_numpy)
        env.pop('CXX',None)

        return env

    def install(self):
        print("****************************************************************************")
        print(self.ctx.site_packages_dir)
        print("****************************************************************************")
        hostpython = sh.Command(self.ctx.hostpython)
        #shprint(hostpython, "setup.py", "install", "--prefix", self.ctx.site_packages_dir)
        self.install_python_package(is_dir=False)


recipe = NewShapely2()
