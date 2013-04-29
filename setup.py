import pelican_bibtex
from distutils.core import setup

CLASSIFIERS = """\
Development Status :: 5 - Production/Stable
Intended Audience :: Science/Research
Intended Audience :: Developers
License :: OSI Approved
Programming Language :: Python
Programming Language :: Python :: 3
Topic :: Software Development
Operating System :: POSIX
Operating System :: Unix

"""

setup(
    name='pelican_bibtex',
    description='A module for estimating Hemodynamical Response Function from functional MRI data',
    long_description=open('Readme.md').read(),
    version=pelican_bibtex.__version__,
    author='Vlad Niculae',
    author_email='vlad@vene.ro',
    url='https://pypi.python.org/pypi/pelican_bibtex',
    py_modules=['pelican_bibtex'],
    classifiers=[_f for _f in CLASSIFIERS.split('\n') if _f],
    license='Public Domain'
)