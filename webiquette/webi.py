#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Define the Webi class
"""

from copy import deepcopy
import logging
import re
import requests
import requests_cache

# from webi.robots_txt import RobotsTxt
import validators

DEFAULT_HEADERS = {"User-Agent": "Webiquette/0.1"}
logger = logging.getLogger(__name__)


class Webi:
    """A well-behaved wrapper around requests and requests_cache."""

    def __init__(
        self,
        netloc: str,
        headers: dict = DEFAULT_HEADERS,
        respect_robots_txt: bool = True,
    ):
        if not validators.domain(netloc):
            raise ValueError(f"Invalid domain/netloc: '{netloc}'.")
        self.netloc = netloc
        if not isinstance(headers, dict):
            raise TypeError(f"Expected dict for headers. Got {type(headers)}.")
        self.headers = deepcopy(headers)
        self.respect_robots_txt = bool(respect_robots_txt)

    def get(self, uri: str):
        if not validators.url(uri):
            raise ValueError(f"Invalid URI: '{uri}'.")
        r = requests.get(uri)
        if r.status_code != 200:
            r.raise_for_status()
        return r
