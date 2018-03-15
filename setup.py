import setuptools

setuptools.setup(
    name='scorer',
    version='0.0.0',
    description='Alternative scorer for the CoNLL-2011/2012 shared tasks on coreference resolution.',
    author='Loïc Grobol',
    author_email='loic.grobol@gmail.com',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    packages=['scorer'],
    install_requires=[
        'docop',
        'scipy',
        'numpy',
    ],
    extras_require={
        'test': ['pytest'],
    },
)
