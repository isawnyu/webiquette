# Webiquette

Wraps "requests" and "requests_cache" for automagical (but configurable) client-side caching, robots.txt compliance, and other good-citizen behavior for bots, scrapers, and scripts.

The `webiquette` package is written and maintained by [Tom Elliott](https://paregorios.org/about/) for the [Institute for the Study of the Ancient World](https://isaw.nyu.edu).
© Copyright 2022 by New York University
Licensed under the AGPL-3.0; see LICENSE.txt file.

## Getting started

```python
>>> from webiquette.webi import Webi

# create a web interface object to manage interations with pleiades.stoa.org
>>> w = Webi(netloc='pleiades.stoa.org')
Using default HTTP Request header for User-Agent = "Webiquette/0.1". We strongly prefer you define your own unique user-agent string and pass it in a headers dict to Webi at initialization.

# customize the request headers our web interface will use
>>> from webiquette.webi import DEFAULT_HEADERS
>>> from pprint import pprint
>>> pprint(DEFAULT_HEADERS, indent=4)
{'User-Agent': 'Webiquette/0.1'}
>> ua = 'WebiquetteDemoBot/0.1'
>> my_headers = {'User-Agent': ua}
>>> w = Webi(netloc='pleiades.stoa.org', headers=my_headers)

# let's peek inside the web interface object
>>> pprint(w.__dict__, indent=4)
{   'headers': {'User-Agent': 'WebiquetteDemoBot/0.1'},
    'netloc': 'pleiades.stoa.org',
    'requests_session': <CachedSession(cache=<SQLiteCache(name=http_cache)>, expire_after=datetime.timedelta(days=30), urls_expire_after=None, allowable_codes=(200,), allowable_methods=('GET', 'HEAD'), stale_if_error=False, cache_control=True)>,
    'respect_robots_txt': True,
    'robots_rules': <webiquette.robots_txt.RobotsRules object at 0x1047c2e90>,
    'user_agent': 'WebiquetteDemoBot/0.1'}
>>> pprint(w.robots_rules.__dict__, indent=4)
{   'rules': {   '*': {   'crawl-delay': ['2'],
                          'disallow': [   '/browse_names',
                                          '/collections/',
                                          '/features/',
                                          '/Members/sgillies/topic-testing/',
                                          '/Members/collections/',
                                          '/names/',
                                          '/login_form',
                                          '/recently_modified',
                                          '/search_kml']},
                 'centurybot': {'disallow': ['/']},
                 'dotbot': {'disallow': ['/']},
                 'istellabot': {'disallow': ['/']},
                 'megaindex.ru': {'disallow': ['/']},
                 'piplbot': {   'disallow': ['/'],
                                'sitemap': [   'http://pleiades.stoa.org/sitemap.xml']},
                 'pleiadesindexerbot': {'crawl-delay': ['1']},
                 'xovibot': {'disallow': ['/']}}}

# use the web interface to fetch some data
>>> r = w.get("https://pleiades.stoa.org/places/295374/json")
>>> type(r)
<class 'requests.models.Response'>
>>> r.json()["title"]
'Zucchabar'

# does local caching work?
>>> r.from_cache
False
>>> r = w.get("https://pleiades.stoa.org/places/295374/json")
>>> r.from_cache
True

# try to fetch something disallowed by robots.txt
>>> r = w.get("https://pleiades.stoa.org/browse_names")
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/Users/foo/Documents/webiquette/webiquette/webi.py", line 137, in get
    raise RobotsDisallowedError(self.user_agent, uri)
webiquette.robots_txt.RobotsDisallowedError: Access to https://pleiades.stoa.org/browse_names disallowed for user-agent:WebiquetteDemoBot/0.1 by robots.txt.

```

## What?