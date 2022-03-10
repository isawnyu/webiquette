#
# This file is part of webiquette
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="webiquette",
    version="0.1",
    author="Tom Elliott",
    author_email="tom.elliott@nyu.edu",
    description=(
        "Wraps 'requests' and 'requests_cache' for automagical (but configurable) "
        "client-side caching, robots.txt compliance, and other good-citizen behavior "
        "for bots, scrapers, and scripts."
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.10.2",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "airtight",
        "requests",
        "requests_cache",
        "textnorm",
        "validators",
    ],
    python_requires=">=3.10.2",
)
