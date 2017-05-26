#!/usr/bin/env python3

from setuptools import setup
import sys

if sys.version_info < (3, 3):
    raise RuntimeError(
        'totp-cli requires python >= 3.3, but this python is %d.%d' %
        sys.version_info[0:2]
    )

setup(
    name='totp',
    description='A cli based TOTP app.',
    long_description=open('README.rst').read(),
    author='Hugo Osvaldo Barrera',
    author_email='hugo@barrera.io',
    url='https://github.com/hobarrera/totp',
    license='MIT',
    packages=['totp'],
    entry_points={
        'console_scripts': [
            'totp = totp:run',
        ]
    },
    install_requires=[
        open('requirements.txt').readlines()
    ],
    use_scm_version={
        'version_scheme': 'post-release',
        # 'write_to': 'totp/version.py',
    },
    setup_requires=['setuptools_scm'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Console :: Curses',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Topic :: Utilities',
    ]
)
