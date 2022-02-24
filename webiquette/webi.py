#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Define the Webi class
"""

from copy import deepcopy
from datetime import timedelta
from http.client import RemoteDisconnected
import logging
from pprint import pformat
import requests
import requests_cache
from textnorm import normalize_space, normalize_unicode
import time
import validators
from webiquette.robots_txt import RobotsRules, RobotsDisallowedError

DEFAULT_CACHE_DIR = "data/cache/"
DEFAULT_EXPIRE_AFTER = timedelta(days=30)
DEFAULT_HEADERS = {"User-Agent": "Webiquette/0.1"}
logger = logging.getLogger(__name__)


def norm(s: str):
    return normalize_space(normalize_unicode(s))


def make_throttle_hook(timeout=1.0):
    """Make a request hook function that adds a custom delay for non-cached requests"""

    def hook(response, *args, **kwargs):
        if not getattr(response, "from_cache", False):
            time.sleep(timeout)
        return response

    return hook


class Webi:
    """A well-behaved wrapper around requests and requests_cache."""

    def __init__(
        self,
        netloc: str,
        headers: dict = DEFAULT_HEADERS,
        respect_robots_txt: bool = True,
        cache_control=True,
        expire_after=DEFAULT_EXPIRE_AFTER,
    ):
        if not validators.domain(netloc):
            raise ValueError(f"Invalid domain/netloc: '{netloc}'.")
        self.netloc = netloc
        if not isinstance(headers, dict):
            raise TypeError(f"Expected dict for headers. Got {type(headers)}.")

        # initialize headers and validate user-agent string
        self.headers = deepcopy(headers)
        for k in ["User-Agent", "user-agent"]:
            try:
                self.user_agent = norm(headers[k])
            except KeyError:
                pass
            else:
                break
        try:
            ua = self.user_agent
        except AttributeError:
            raise ValueError("Headers did not include User-Agent.")
        else:
            if ua == "":
                raise ValueError(
                    "Headers contained blank/whitespace-only user-agent string."
                )
            elif ua == DEFAULT_HEADERS["User-Agent"]:
                logger.warning(
                    f'Using default HTTP Request header for User-Agent = "{ua}". '
                    "We strongly prefer you define your own unique user-agent string "
                    "and pass it in a headers dict to Webi at initialization."
                )

        # initialize robots.txt functionality for this netloc
        self.respect_robots_txt = bool(respect_robots_txt)
        if respect_robots_txt:
            self.robots_rules = RobotsRules(netloc=self.netloc, headers=self.headers)

        # set up caching for this netloc
        cache_path = DEFAULT_CACHE_DIR + netloc.replace(".", "_")
        # see https://requests-cache.readthedocs.io/en/stable/user_guide/expiration.html
        if not cache_control and not expire_after:
            self.requests_session = requests_cache.CachedSession(cache_path)
        elif cache_control and not expire_after:
            self.requests_session = requests_cache.CachedSession(
                cache_path, cache_control=cache_control
            )
        elif not cache_control and expire_after:
            self.requests_session = requests_cache.CachedSession(
                cache_path, expire_after=expire_after
            )
        else:
            self.requests_session = requests_cache.CachedSession(
                cache_path, cache_control=cache_control, expire_after=expire_after
            )

        # set up crawl-delay if needed
        try:
            crawl_delay = self.robots_rules.crawl_delay(self.user_agent)
        except AttributeError:
            crawl_delay = 0
        if crawl_delay > 0:
            delay_seconds = (
                float(crawl_delay) / 1000.0
            )  # robots uses integer milliseconds; time.sleep uses float seconds
            self.requests_session.hooks["response"].append(
                make_throttle_hook(delay_seconds)
            )

    def get(
        self,
        uri: str,
        additional_headers: dict = dict(),
        bypass_cache=False,
        retries=4,
        backoff_step=2,
    ):
        """Use HTTP get to resolve URI, observing robots.txt rules and prefering cache."""
        if not validators.url(uri):
            raise ValueError(f"Invalid URI: '{uri}'.")
        if self.respect_robots_txt:
            if not self.robots_rules.allowed(self.user_agent, uri):
                raise RobotsDisallowedError(self.user_agent, uri)
        if additional_headers:
            headers = deepcopy(self.headers)
            for k in additional_headers.keys():
                headers[k] = additional_headers[k]
        else:
            headers = self.headers
        backoff = 1
        tries = 0
        while True:
            try:
                r = self._get(uri, headers, bypass_cache)
            except RemoteDisconnected:
                if tries >= retries:
                    raise
                tries += 1
                backoff = backoff * backoff_step
                logger.error(
                    f"Remote server disconnected unexpectedly. Sleeping {backoff} seconds before retrying ..."
                )
                time.sleep(backoff)
            else:
                break
        if r.status_code != 200:
            r.raise_for_status()
        logger.debug(f"Response headers:\n{pformat(r['headers'], indent=4)}")
        return r

    def _get(self, uri, headers, bypass_cache):
        if bypass_cache:
            r = requests.get(uri, headers=headers)
        else:
            r = self.requests_session.get(uri, headers=headers)
        return r
