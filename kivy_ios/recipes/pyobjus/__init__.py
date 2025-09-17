from kivy_ios.toolchain import CythonRecipe


class PyobjusRecipe(CythonRecipe):
    version = "master"
    #url = "https://github.com/kivy/prasadmadanayake/archive/{version}.zip"
    url = "https://github.com/prasadmadanayake/pyobjus/archive/{version}.zip"
    library = "libpyobjus.a"
    depends = ["python"]
    pre_build_ext = True


recipe = PyobjusRecipe()
