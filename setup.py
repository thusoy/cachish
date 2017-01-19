#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from setuptools import setup, find_packages

install_requires = [
    'flask',
    'pyyaml',
    'requests',
]

setup(
    name='cachish',
    version='1.1.1',
    author='Tarjei Husøy',
    author_email='git@thusoy.com',
    url='https://github.com/thusoy/cachish',
    description="Stale cache-ish thingie",
    packages=find_packages(),
    install_requires=install_requires,
    extras_require={
        'gunicorn': [
            'gunicorn',
            'gevent',
        ]
    },
    classifiers=[
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Environment :: Web Environment',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        # 'Programming Language :: Python :: 2.6',
        # 'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
)
