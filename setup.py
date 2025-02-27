# setup.py
from setuptools import setup

setup(
    name="heic2img-converter",
    version="0.1.1",
    description="Simple CLI tool to convert HEIC files to JPG, PNG, or WebP",
    author="John Watters <john@johnwatters.com>",
    py_modules=["heic2img"],
    install_requires=["tqdm>=4.65.0", "pillow>=10.0.0", "pillow-heif>=0.19.0"],
    entry_points={"console_scripts": ["heic2img=heic2img:main:main"]},
)
