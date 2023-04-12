#
# This file is part of webiquette
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Test the webiquette.webi module
"""

from webiquette.robots_txt import RobotsDisallowedError
from webiquette.webi import Webi, DEFAULT_HEADERS
import pytest
import requests_cache

requests_cache.install_cache("tests/tests_cache")


class TestInit:
    def test_init_no_args(self):
        with pytest.raises(TypeError):
            Webi()

    def test_init_netloc(self):
        netloc = "pleiades.stoa.org"
        w = Webi(netloc=netloc)
        assert w.netloc == netloc
        assert w.headers == DEFAULT_HEADERS
        assert w.respect_robots_txt == True

    def test_init_netloc_bad(self):
        with pytest.raises(ValueError):
            Webi(netloc="pleiades")

    def test_init_custom(self):
        netloc = "pleiades.stoa.org"
        headers = {
            "User-Agent": "CustomBot/7.9",
            "Referer": "http://nowhere.com/strange_brew",
        }
        respect = False
        w = Webi(netloc=netloc, headers=headers, respect_robots_txt=respect)
        assert w.netloc == netloc
        assert w.headers == headers
        assert w.respect_robots_txt == False


class TestGet:
    def test_get_allowed(self):
        netloc = "pleiades.stoa.org"
        w = Webi(netloc=netloc)
        r = w.get("https://pleiades.stoa.org/places/295374")
        assert r.status_code == 200

    def test_get_disallowed(self):
        netloc = "pleiades.stoa.org"
        w = Webi(netloc=netloc)
        with pytest.raises(RobotsDisallowedError):
            r = w.get("https://pleiades.stoa.org/login_form")


class TestHead:
    def test_head_allowed(self):
        netloc = "pleiades.stoa.org"
        w = Webi(netloc=netloc)
        r = w.head("https://pleiades.stoa.org/places/295374")
        assert r.status_code == 200

    def test_head_disallowed(self):
        netloc = "pleiades.stoa.org"
        w = Webi(netloc=netloc)
        with pytest.raises(RobotsDisallowedError):
            r = w.head("https://pleiades.stoa.org/login_form")
