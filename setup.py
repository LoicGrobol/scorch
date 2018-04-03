import setuptools

setuptools.setup(
    packages=['scorch'],
    install_requires=[
        'docopt',
        'scipy',
        'numpy',
    ],
    extras_require={
        'test': ['pytest'],
    },
    entry_points={
    'console_scripts': [
        'scorch=scorch.scorch:main_entry_point',
    ],
},
)
