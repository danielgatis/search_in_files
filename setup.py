from codecs import open
from os import path

from setuptools import Extension, find_packages, setup

here = path.abspath(path.dirname(__file__))


with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='search_in_files',
    version='0.0.6',
    description='A tool for find text in files.',
    long_description=long_description,
    url='https://github.com/danielgatis/search_in_files',
    author='Daniel Gatis',
    author_email='danielgatis@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
    keywords='python file-search text-search fast',
    setup_requires=['cython'],
    install_requires=['six'],
    packages = find_packages(exclude=['notebooks']),
    ext_modules=[
        Extension(
            'search_in_files.csearch',
            sources=['search_in_files/csearch.pyx'],
        ),
    ],
    entry_points={
        'console_scripts': [
            'search_in_files = search_in_files.search:main'
        ]
    },
)
