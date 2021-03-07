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
    description='The PrecFOAM wrapper for SimDOME',
    keywords='SimDOME, cuds, precipitation, NMC hydroxide',
    long_description=README_TEXT,
    install_requires=[
        'osp-core>=' + OSP_CORE_MIN + ', <' + OSP_CORE_MAX,
    ],
    packages=find_packages(exclude=("examples")),
    include_package_data=True,
    # entry_points={
    #     'wrappers':
    #         'precfoam = osp.wrappers.prec_nmc_wrappers:PrecFoamSession'},
)
