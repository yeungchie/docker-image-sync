from pathlib import Path
from setuptools import setup, find_packages

here = Path(__file__).resolve().parent

with open(here / 'README.md', encoding='utf-8') as f:
    long_description = '\n' + f.read()

VERSION = '0.0.2'
DESCRIPTION = 'Docker Image Synchronizer'

setup(
    name='docker-image-sync',
    version=VERSION,
    author='YEUNGCHIE',
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yeungchie/docker-image-sync',
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=[
        'PyYAML>=5.3.1',
        'docker>=5.0.3',
        'rich>=12.6.0',
    ],
    keywords=['python', 'docker', 'image', 'sync', 'linux'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
    ],
)
