import os
import subprocess
import sys

from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext

from parametric_plasma_source.build_python import build as build_python

class CMakeExtention(Extension):
    def __init__(self, name, sourcedir=""):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    def run(self):
        try:
            subprocess.check_output(["cmake", "--version"])
        except OSError:
            raise RuntimeError("CMake must be installed to build the "
                               "following extentions: "
                               ", ".join(e.name for e in self.extensions))

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(
            os.path.dirname(self.get_ext_fullpath(ext.name))
        )
        if not extdir.endswith(os.path.sep):
            extdir += os.path.sep

        cmake_args = ["-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=" + extdir,
                      "-DPYTHON_EXECUTABLE=" + sys.executable]

        cfg = "Debug" if self.debug else "Release"
        build_args = ["--config", cfg]

        cmake_args += ["-DCMAKE_BUILD_TYPE=" + cfg]
        build_args += ["--", "-j2"]
        build_args += ["plasma_source"]

        env = os.environ.copy()
        env["CXXFLAGS"] = "{} -DVERSION_INFO=\\\"{}\\\"".format(
            env.get("CXXFLAGS", ""),
            self.distribution.get_version()
        )

        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        subprocess.check_call(
            ["cmake", ext.sourcedir] + cmake_args,
            cwd=self.build_temp,
            env=env
        )
        subprocess.check_call(
            ["cmake", "--build", "."] + build_args,
            cwd=self.build_temp
        )


with open("README.md", "r") as fh:
    long_description = fh.read()

build_python(source_dir="parametric_plasma_source")

setup(
    name="parametric_plasma_source",
    version="0.0.6",
    author="Jonathan Shimwell",
    author_email="jonathan.shimwell@ukaea.uk",
    description="Parametric plasma source for fusion simulations in OpenMC",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shimwell/parametric_plasma_source",
    packages=find_packages(),
    ext_modules=[CMakeExtention("parametric_plasma_source/plasma_source")],
    cmdclass=dict(build_ext=CMakeBuild),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
