#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Define the Webi class
"""

from copy import deepcopy
import logging
import requests
import requests_cache
import validators
from webiquette.robots_txt import RobotsRules, RobotsDisallowedError

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
        for k in ["User-Agent", "user-agent"]:
            try:
                self.user_agent = headers[k]
            except KeyError:
                pass
            else:
                break
        try:
            self.user_agent
        except AttributeError:
            raise ValueError("Headers did not include User-Agent.")
        self.respect_robots_txt = bool(respect_robots_txt)
        if respect_robots_txt:
            self.robots_rules = RobotsRules(netloc=self.netloc, headers=self.headers)

    def get(self, uri: str):
        """Use HTTP get to resolve URI, observing robots.txt rules and prefering cache."""
        if not validators.url(uri):
            raise ValueError(f"Invalid URI: '{uri}'.")
        if self.respect_robots_txt:
            if not self.robots_rules.allowed(self.user_agent, uri):
                raise RobotsDisallowedError(self.user_agent, uri)
        r = requests.get(uri)
        if r.status_code != 200:
            r.raise_for_status()
        return r
