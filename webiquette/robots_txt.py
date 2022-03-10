#
# This file is part of webiquette
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

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
        d = dict()
        if r.status_code != 200:
            logger.warning(f"No robots.txt found for {netloc}.")
        else:
            lines = [normalize_space(l) for l in r.text.split("\n")]
            lines = [l for l in lines if l != ""]
            if len(lines) == 1 and len(lines[0].split(":")) > 2:
                lines = [normalize_space(l) for l in r.text.split("\\n")]  # idai
            if len(lines) == 1 and len(lines[0].split(":")) > 2:
                raise RuntimeError("only one line")
            if len(lines) == 0:
                logger.warning(f"Empty robots.txt found for {netloc}.")
            else:
                lines = [l.replace('"', "") for l in lines]  # idai
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
        ua = self._clean_user_agent(user_agent)
        user_agents = ["*"]
        if ua != "*":
            user_agents.append(ua)
        for ua in user_agents:
            try:
                rules = self.rules[ua]
            except KeyError:
                continue
            else:
                try:
                    disallow = rules["disallow"]
                except KeyError:
                    continue
                else:
                    for path in disallow:
                        if parts.path.startswith(path):
                            return False
        return True

    def crawl_delay(self, user_agent: str):
        ua = self._clean_user_agent(user_agent)
        user_agents = ["*"]
        if ua != "*":
            user_agents.append(ua)
        crawl_delay = 0
        for ua in user_agents:
            try:
                rules = self.rules[ua]
            except KeyError:
                continue
            else:
                try:
                    crawl_delay = rules["crawl-delay"]
                except KeyError:
                    continue
        if isinstance(crawl_delay, list):
            if len(crawl_delay) == 1:
                crawl_delay = crawl_delay[0]
            else:
                raise RuntimeError(
                    f"Unsupported crawl_delay multi-value list for user_agent={ua}: {crawl_delay}"
                )
        if isinstance(crawl_delay, str):
            crawl_delay = int(crawl_delay)
        logger.debug(crawl_delay)
        return crawl_delay

    def _clean_user_agent(self, user_agent: str):
        clean_user_agent = normalize_space(
            [ua for ua in user_agent.lower().split("(") if ua.strip() != ""][0]
        )
        clean_user_agent = [
            ua for ua in clean_user_agent.split("/") if ua.strip() != ""
        ][0].strip()
        return clean_user_agent
