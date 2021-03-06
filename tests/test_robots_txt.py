#
# This file is part of webiquette
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Test the webiquette.robots_txt module
"""

from webiquette.robots_txt import RobotsRules
from webiquette.webi import DEFAULT_HEADERS
import pytest
import requests_cache

requests_cache.install_cache("tests/tests_cache")


class TestInit:
    def test_init_no_args(self):
        with pytest.raises(TypeError):
            RobotsRules()

    def test_init(self):
        netloc = "pleiades.stoa.org"
        r = RobotsRules(netloc=netloc, headers=DEFAULT_HEADERS)
        assert isinstance(r.rules, dict)
        assert isinstance(r.rules["*"], dict)
        assert isinstance(r.rules["pleiadesindexerbot"], dict)


class TestAllowed:
    def test_allowed_all(self):
        r = RobotsRules(netloc="pleiades.stoa.org", headers=DEFAULT_HEADERS)
        uri = "https://pleiades.stoa.org/places/295374"
        assert r.allowed("*", uri)

    def test_allowed_default_ua(self):
        r = RobotsRules(netloc="pleiades.stoa.org", headers=DEFAULT_HEADERS)
        uri = "https://pleiades.stoa.org/places/295374"
        assert r.allowed(DEFAULT_HEADERS["User-Agent"], uri)

    def test_disallowed_all(self):
        r = RobotsRules(netloc="pleiades.stoa.org", headers=DEFAULT_HEADERS)
        uri = "https://pleiades.stoa.org/login_form"
        assert not r.allowed("*", uri)
        assert not r.allowed(DEFAULT_HEADERS["User-Agent"], uri)

    def test_disallowed_specific(self):
        r = RobotsRules(netloc="pleiades.stoa.org", headers=DEFAULT_HEADERS)
        uri = "https://pleiades.stoa.org/places/295374"
        assert not r.allowed("istellabot", uri)


class TestOneLinerRobots:
    def test_idai(self):
        r = RobotsRules(netloc="gazetteer.dainst.org", headers=DEFAULT_HEADERS)
        assert isinstance(r.rules, dict)
        assert isinstance(r.rules["*"], dict)
