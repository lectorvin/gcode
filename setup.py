import os
import sys
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


if sys.version_info >= (3, ):
    raise SystemError('Nope! Try python2.7 or older')

setup(
    name = "Gcode",
    version = "0.1",
    packages = find_packages(),
    install_requires = [
        'numpy>=1.8',
        'matplotlib>=1.3',
        'pandas',
        'PIL',
        'images2gif'
    ],
    package_data = {
        '':['*.txt']
    },
    
    author = "lectorvin",
    description = "Gcode parser",
    license = "WTFPL",
    long_description = read("README.md")
)
