import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "Gcode",
    version = "0.3",
    packages = find_packages(),
    install_requires = [
        'numpy>=1.8',
        'pyqtgraph'
    ],
    package_data = {
        '':['*.txt']
    },

    author = "lectorvin",
    description = "Gcode parser",
    license = "WTFPL",
    long_description = read("README.md")
)
