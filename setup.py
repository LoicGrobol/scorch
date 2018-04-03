import setuptools

setuptools.setup(
    name='scorch',
    version='0.0.2',
    description='Alternative scorer for the CoNLL-2011/2012 shared tasks on coreference resolution.',
    url='https://github.com/LoicGrobol/scorch',
    author='Loïc Grobol',
    author_email='loic.grobol@gmail.com',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
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
