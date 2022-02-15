#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Define RobotsTxt class
"""

import logging
import requests
from textnorm import normalize_space
from urllib.parse import urlparse, urlunparse
import validators

logger = logging.getLogger(__name__)


class RobotsDisallowedError(Exception):
    def __init__(self, user_agent, uri):
        self.message = (
            f"Access to {uri} disallowed for user-agent:{user_agent} by robots.txt."
        )
        super().__init__(self.message)


class RobotsRules:
    """Parse and answer questions about rules in a robots.txt file for a particular netloc."""

    def __init__(self, netloc: str, headers: dict):
        if not validators.domain(netloc):
            raise ValueError(f"Invalid domain/netloc: '{netloc}'.")
        for scheme in ["https", "http"]:
            uri = urlunparse((scheme, netloc, "/robots.txt", "", "", ""))
            r = requests.get(uri)
            if r.status_code == 200:
                break
        if r.status_code != 200:
            r.raise_for_status()
        d = dict()
        lines = [normalize_space(l) for l in r.text.split("\n")]
        lines = [l for l in lines if l != ""]
        for line in lines:
            k, v = [p.strip() for p in line.split(": ")]
            k = k.lower()
            if k == "user-agent":
                ua = v.lower()
                d[ua] = dict()
            else:
                try:
                    d[ua][k]
                except KeyError:
                    d[ua][k] = list()
                d[ua][k].append(v)
        self.rules = d

    def allowed(self, user_agent: str, uri: str):
        """Is uri allowed for this user_agent by robots.txt?"""
        parts = urlparse(uri)
        clean_user_agent = normalize_space(
            [ua for ua in user_agent.lower().split("(") if ua.strip() != ""][0]
        )
        clean_user_agent = [
            ua for ua in clean_user_agent.split("/") if ua.strip() != ""
        ][0].strip()
        user_agents = ["*", clean_user_agent]
        user_agents = list(set(user_agents))
        for ua in user_agents:
            try:
                rules = self.rules[ua]
            except KeyError:
                pass
            else:
                try:
                    disallow = rules["disallow"]
                except KeyError:
                    pass
                else:
                    for path in disallow:
                        if parts.path.startswith(path):
                            return False
        return True
