#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test the webiquette.webi module
"""

from webiquette.webi import Webi, DEFAULT_HEADERS
import pytest


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
