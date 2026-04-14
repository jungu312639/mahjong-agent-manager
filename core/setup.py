from setuptools import setup, Extension
import pybind11
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

ext_modules = [
    Extension(
        "tw_ukeire_cpp",
        [
            "engine/tw_shanten.cpp", 
            "engine/tw_ukeire.cpp",
            "sandbox/tactics.cpp"
        ],
        include_dirs=[pybind11.get_include(), "include"],
        language="c++",
        extra_compile_args=["-O3", "-std=c++17"],
    )
]

setup(
    name="tw_ukeire_cpp",
    ext_modules=ext_modules,
)
