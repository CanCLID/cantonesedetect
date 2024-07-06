from setuptools import setup, find_packages
from pathlib import Path

# read the contents of your README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Import version from version.py
from cantonesedetect.version import __version__

setup(
    name='cantonesedetect',
    version=__version__,
    description='A minimal package that detect Cantonese sentences in Traditional Chinese text.',
    author='Chaak Ming Lau, Mingfei Lau and Ann Wai Huen To',
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type='text/markdown',
    test_suite='tests',
    entry_points={
        'console_scripts': [
            'cantonesedetect=cantonesedetect.cli:main',
        ],
    },
)
