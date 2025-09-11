
from kivy_ios.toolchain import Recipe

class OpenCVExtrasRecipeV2(Recipe):
    """
    OpenCV extras recipe allows us to build extra modules from the
    `opencv_contrib` repository. It depends on opencv recipe and all the build
    of the modules will be performed inside opencv recipe build directory.
    .. note:: the version of this recipe should be the same than opencv recipe.
    .. warning:: Be aware that these modules are experimental, some of them
        maybe included in opencv future releases and removed from extras.
    .. seealso:: https://github.com/opencv/opencv_contrib
    """
    version = '4.12.0'
    url = 'https://github.com/opencv/opencv_contrib/archive/{version}.zip'

    def prebuild_platform(self, plat):
        if self.has_marker("patched"):
            return
        self.apply_patch("ios_conversion.patch")
        self.set_marker("patched")


recipe = OpenCVExtrasRecipeV2()