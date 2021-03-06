from setuptools import setup, find_packages

from packageinfo import VERSION, NAME, OSP_CORE_MIN, OSP_CORE_MAX

# Read description
with open('README.md', 'r') as readme:
    README_TEXT = readme.read()

# main setup configuration class
setup(
    name=NAME,
    version=VERSION,
    author='MuSyChEn research group at Politecnico di Torino',
    description='A collection of wrappers for wet-phase synthesis of Ni-Mn-Co hydroxide',
    keywords='SimDOME, CUDS, Precipitation, NMC hydroxide',
    long_description=README_TEXT,
    install_requires=[
        'osp-core>=' + OSP_CORE_MIN + ', <' + OSP_CORE_MAX,
    ],
    packages=find_packages(exclude=("examples")),
    include_package_data=True,
    # entry_points={
    #     'wrappers':
    #         ''},
)
