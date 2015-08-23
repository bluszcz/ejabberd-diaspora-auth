# -*- coding: utf-8 -*-
import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='ejabberd-diaspora-auth',
    version='0.0.1',
    packages=['ejabberd_diaspora_auth'],
    include_package_data=True,
    license='Apache License version 2.0',
    description='Ejabberd external authentication trough diaspora* database.',
    long_description=README,
    url='https://github.com/bluszcz/ejabberd-diaspora-auth',
    author='Rafał Zawadzki',
    author_email='bluszcz@bluszcz.net',
    classifiers=[
        'Environment :: Console',
        'Topic :: Communications :: Chat',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License', 
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        ],
)

