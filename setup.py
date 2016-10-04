#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.6',
    # TODO: put package requirements here
    'colorclass>=2.2.0',
    'terminaltables>=3.0.0',
    'wrapt>=1.10.8',
    'babel>=2.3.4',
    'pyyaml==3.11',
]

test_requirements = [
    'pytest>=2.9.2',
    'pytest-cov>=2.2.1',
    # TODO: put package test requirements here
]

setup_requirements = [
    'pytest-runner',
]

setup(
    name='jobcalc',
    version='0.1.1',
    description="Job calculator utilities and command line application.",
    long_description=readme + '\n\n' + history,
    author="Michael Housh",
    author_email='mhoush@houshhomeenergy.com',
    url='https://github.com/m-housh/jobcalc',
    packages=find_packages(),
    package_dir={'jobcalc':
                 'jobcalc'},
    entry_points={
        'console_scripts': [
            'job-calc=jobcalc.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    setup_requires=setup_requirements,
    license="MIT license",
    zip_safe=False,
    keywords='jobcalc',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='jobcalc/test',
    tests_require=test_requirements
)
