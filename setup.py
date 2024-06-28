from setuptools import setup, find_packages

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='cantonesedetect',
    version='1.0',
    description='A minimal package that detect Cantonese sentences in Traditional Chinese text.',
    author='Chaak Ming Lau, Mingfei Lau and Ann Wai Huen To',
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type='text/markdown'
)