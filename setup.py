from setuptools import setup, find_packages

from tanew.__init__ import __version__ as VERSION

setup(
    name='quine-archive',
    version=VERSION,
    description="hmmm",
    long_description="tbd",
    license='MIT',
    author='Matthew Barber',
    author_email='quitesimplymatt@gmail.com',
    url='https://github.com/Honno/quine/',
    classifiers=[
        'Programming Language :: Python :: 3'
    ],
    keywords='quine',
    packages=find_packages(),
)
