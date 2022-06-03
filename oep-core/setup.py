#!/usr/bin/env python

from setuptools import find_packages, setup

setup(
    name='oep-core',
    version='0.7.0',
    description='oep Core',
    long_description='oep Core utilities for various projects',
    author='Declan Keyes-Bevan',
    author_email='declan@oep.com',
    url='https://www.oep.com',
    packages=find_packages(),
    install_requires=[
        'aws-psycopg2',
        'boto3',
        'botocore',
        'requests',
    ],
    python_requires='>=3.7'
)
