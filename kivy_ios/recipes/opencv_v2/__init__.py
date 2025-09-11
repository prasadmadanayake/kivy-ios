# pure-python package, this can be removed when we'll support any python package
import glob
import shutil, os, shlex
from os import listdir
from os.path import join
from pathlib import Path

import sh

from kivy_ios.context_managers import cd
from kivy_ios.toolchain import Recipe, shprint, cache_execution


class OpenCV_V2(Recipe):
    version = "4.12.0"
    url = "https://github.com/opencv/opencv/archive/refs/tags/{version}.zip"

    depends = ["python", "opencv_extras_v2", "numpy"]
    libraries = [
        "build_xcframework/lib/python3/cv2.a"
    ]
    disable = [
        "highgui", "gapi", "dnn", "java", "java_bindings_generator", "apps", "freetype", "hdf", "python2"
    ]
    pbx_frameworks = ["AVFoundation", "UIKit", "CoreGraphics", "CoreImage", "CoreMedia", "QuartzCore", "Foundation"]

    @staticmethod
    def copy_files(src, dest):
        files = listdir(src)
        for fname in files:
            shutil.copy2(join(src, fname), dest)

    def prebuild_platform(self, plat):
        if self.has_marker("patched"):
            return
        self.apply_patch("opencv-4.12.0-kivy.patch")
        self.set_marker("patched")

    def build_platform(self, plat):
        opencv_extras_dir = self.get_recipe(
            'opencv_extras_v2', self.ctx).get_build_dir(plat)
        opencv_extras = [
            f'-DOPENCV_EXTRA_MODULES_PATH={opencv_extras_dir}/modules',
            '-DBUILD_opencv_legacy=OFF',
        ]

        env = self.get_recipe_env(plat)
        python_major = self.ctx.python_recipe.version[0]
        python_recipe = self.get_recipe('python3', self.ctx)
        python_include_files = join(self.ctx.dist_dir, "hostpython3", "include")
        python_include_files_dirs = glob.glob(
            '{}/{}'.format(python_include_files, "python{}.*".format(python_major)), recursive=False)
        if len(python_include_files_dirs) > 0:
            python_include_root = python_include_files_dirs[0]
        else:
            python_include_root = python_include_files

        os_specific_numpy_def_dirs = glob.glob('{}/numpy/{}/numpy-*/build/src.macosx-*/numpy/core/include'.format(
            python_recipe.ctx.build_dir,
            plat.name
        ))
        os_specific_numpy_defs = os_specific_numpy_def_dirs[0]

        python_site_packages = python_recipe.ctx.site_packages_dir
        python_link_root = join(self.ctx.dist_dir, "lib")
        print(python_link_root)
        python_link_version = python_major
        python_library = join(python_link_root,
                              'libpython{}.a'.format(python_link_version))
        python_include_numpy = join(self.ctx.dist_dir, "include", "common",
                                    'numpy')

        build_xcframework = join(self.build_dir, "build_xcframework")
        shprint(sh.mkdir, build_xcframework)
        with cd(build_xcframework):
            shutil.copytree(python_include_numpy, "numpy")
            self.copy_files(join(os_specific_numpy_defs, "numpy"), "numpy/numpy")

            python_include_numpy = join(build_xcframework, "numpy")

            shprint(sh.cmake,
                    # "-GXcode",
                    "-DCMAKE_BUILD_TYPE=Release",
                    "-DCMAKE_C_FLAGS=-fembed-bitcode",
                    "-DCMAKE_CXX_FLAGS=-fembed-bitcode",
                    "-DWITH_OPENCL=OFF",
                    "-DBUILD_opencv_hdf=OFF",
                    "-DCMAKE_CXX_COMPILER_WORKS=TRUE",
                    "-DCMAKE_C_COMPILER_WORKS=TRUE",
                    "-DCMAKE_AR={}".format(env["AR"]),
                    "-DIOS=1",
                    "-DCMAKE_VERBOSE_MAKEFILE:BOOL=ON",
                    "-DCMAKE_OSX_SYSROOT={}".format(plat.sysroot),
                    "-DCMAKE_OSX_ARCHITECTURES={}".format(plat.arch),
                    '-DIOS_ARCH={}'.format(plat.arch),
                    '-DIPHONEOS_DEPLOYMENT_TARGET={}'.format("12.0"),
                    '-DCMAKE_SHARED_LINKER_FLAGS="-L{path} -lpython{version}"'.format(
                        path=python_link_root,
                        version=python_link_version),
                    '-DBUILD_WITH_STANDALONE_TOOLCHAIN=ON',
                    '-DBUILD_SHARED_LIBS=OFF',
                    '-DBUILD_opencv_highgui=OFF',
                    '-DBUILD_STATIC_LIBS=ON',
                    '-DWITH_CAROTENE=OFF',
                    '-DBUILD_opencv_gapi=OFF',
                    '-DBUILD_opencv_dnn=OFF',
                    '-DBUILD_opencv_java=OFF',
                    '-DBUILD_opencv_java_bindings_generator=OFF',
                    '-DBUILD_opencv_highgui=OFF',
                    '-DBUILD_TESTS=OFF',
                    '-DBUILD_PERF_TESTS=OFF',
                    '-DENABLE_TESTING=OFF',
                    '-DBUILD_EXAMPLES=OFF',
                    '-DBUILD_ANDROID_EXAMPLES=OFF',
                    #"-DOpenCV_BINARY_DIR={}".format(build_lib_dir),
                    #"-DOPENCV_PYTHON_STANDALONE_INSTALL_PATH={}".format(build_lib_dir),
                    "-DOpenCV_SOURCE_DIR={}".format(self.build_dir),
                    "-DBUILD_opencv_python3=ON",
                    "-DBUILD_opencv_python2=OFF",
                    "-DOPENCV_PYTHON3_INSTALL_PATH=python",
                    "-DINSTALL_CREATE_DISTRIB=ON",
                    "-DBUILD_opencv_apps=OFF",
                    "-DBUILD_opencv_freetype=OFF",
                    "-DBUILD_DOCS=OFF",
                    "-DBUILD_OPENEXR=ON",
                    "-DBUILD_PNG=ON",
                    "-DOPENCV_PYTHON_SKIP_DETECTION=ON",
                    "-DPYTHON3INTERP_FOUND=ON",
                    "-DPYTHON_DEFAULT_AVAILABLE=ON",
                    '-DPYTHON_DEFAULT_EXECUTABLE={}'.format(self.ctx.hostpython),
                    '-DPYTHON{major}_EXECUTABLE={host_python}'.format(
                        major=python_major, host_python=self.ctx.hostpython),
                    '-DPYTHON_EXECUTABLE={host_python}'.format(host_python=self.ctx.hostpython),
                    '-DPYTHON{major}_INCLUDE_PATH={include_path}'.format(
                        major=python_major, include_path=python_include_root),
                    '-DPYTHON_INCLUDE_DIRS={include_path}'.format(include_path=python_include_root),
                    '-DPYTHON{major}_LIBRARIES={python_lib}'.format(
                        major=python_major, python_lib=python_library),
                    '-DPYTHON_LIBRARY={python_lib}'.format(python_lib=python_library),
                    '-DPYTHON{major}_NUMPY_INCLUDE_DIRS={numpy_include}'.format(
                        major=python_major, numpy_include=python_include_numpy),
                    '-DPYTHON_NUMPY_INCLUDE_DIRS={numpy_include}'.format(numpy_include=python_include_numpy),
                    '-DPYTHON{major}_PACKAGES_PATH={site_packages}'.format(
                        major=python_major, site_packages=python_site_packages),
                    '-DPYTHON_PACKAGES_PATH={site_packages}'.format(site_packages=python_site_packages),
                    *opencv_extras,

                    self.build_dir,
                    _env=env)

            # link = join(build_dir, "modules", "python3", "CMakeFiles", "opencv_python3.dir", "link.txt")
            #
            # with open(link, "w") as fs:
            #     cv2_objs = [
            #         "CMakeFiles/opencv_python3.dir/__/src2/cv2.cpp.o",
            #         "CMakeFiles/opencv_python3.dir/__/src2/cv2_util.cpp.o",
            #         "CMakeFiles/opencv_python3.dir/__/src2/cv2_numpy.cpp.o",
            #         "CMakeFiles/opencv_python3.dir/__/src2/cv2_convert.cpp.o",
            #         "CMakeFiles/opencv_python3.dir/__/src2/cv2_highgui.cpp.o"
            #     ]
            #
            #     linker_args = "{} qc {} {}".format(
            #         env["AR"],
            #         "../../lib/python3/cv2.a",
            #         " ".join(cv2_objs)
            #     )
            #     fs.write(linker_args)
            shprint(sh.make, self.ctx.concurrent_make,)

    def postbuild_platform(self, plat):
        output_dir = join(self.get_build_dir(plat), "build_xcframework")
        cv_libs = sorted(str(p.resolve()) for p in Path(os.path.join(output_dir, "lib")).glob("*.a"))
        external_libs = sorted(str(p.resolve()) for p in Path(os.path.join(output_dir, "3rdparty/lib")).glob("*.a"))
        cv_dir = join(output_dir,"modules/python3/CMakeFiles/opencv_python3.dir/__/src2")
        cv2_objs = [
            join(cv_dir, "cv2.cpp.o"),
            join(cv_dir, "cv2_util.cpp.o"),
            join(cv_dir, "cv2_numpy.cpp.o"),
            join(cv_dir, "cv2_convert.cpp.o"),
            join(cv_dir, "cv2_highgui.cpp.o")
        ]

        cmd = ["-static", "-o", join(output_dir, "lib/python3/cv2.a")] + cv2_objs + cv_libs + external_libs
        shprint(sh.libtool, *cmd)
        pass

    @cache_execution
    def install_sources(self):
        self.install_python_binding()
        pass

    def install_python_binding(self):
        self.mock_libs("cv2")
        arch = list(self.platforms_to_build)[0]
        build_dir = self.get_build_dir(arch)
        loader_root = join(build_dir, "build_xcframework", "python_loader")
        if arch:
            with cd(loader_root):
                hostpython = sh.Command(self.ctx.hostpython)
                build_env = arch.get_env()
                dest_dir = join(self.ctx.dist_dir, "root", "python3")
                build_env['PYTHONPATH'] = self.ctx.site_packages_dir
                shprint(hostpython, "setup.py", "install", "--prefix", dest_dir, _env=build_env)

    def mock_libs(self, lib):
        file = "{}.cpython-{}{}-darwin.so".format(lib, self.ctx.python_recipe.version[0],
                                                  self.ctx.python_recipe.version[2])
        shprint(sh.touch, join(self.ctx.site_packages_dir, file))


recipe = OpenCV_V2()
