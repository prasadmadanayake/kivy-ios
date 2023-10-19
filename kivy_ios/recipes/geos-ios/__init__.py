import shutil
from os.path import join

import sh

from kivy_ios.context_managers import cd
from kivy_ios.toolchain import Recipe, shprint


class GeosIOSRecipe(Recipe):
    version = "3.11.0"
    url = "https://github.com/libgeos/geos/archive/{version}.zip"
    libraries = ["cmake-build/lib/libgeos.a", "cmake-build/lib/libgeos_c.a"]
    depends = ["python"]
    include_dir = "include"
    include_per_arch = True

    def build_platform(self, plat):
        env = self.get_recipe_env(plat)
        shprint(sh.cmake,
                "-DCMAKE_BUILD_TYPE=Release",
                "-DBUILD_SHARED_LIBS=OFF",
                "-DCMAKE_AR={}".format(env["AR"]),
                "-DCMAKE_OSX_SYSROOT={}".format(plat.sysroot),
                "-DCMAKE_OSX_ARCHITECTURES={}".format(plat.arch),
                "-DCMAKE_OSX_DEPLOYMENT_TARGET={}".format("9.0"),
                "-B cmake-build",
                "-S .",
                _env=env
                )
        with cd("cmake-build"):
            shprint(sh.make, "clean")
            shprint(sh.make, self.ctx.concurrent_make, "geos_c")
        shutil.copyfile(join(self.build_dir, "cmake-build", "capi", "geos_c.h"),
                        join(self.build_dir, "include", "geos_c.h"))



recipe = GeosIOSRecipe()
