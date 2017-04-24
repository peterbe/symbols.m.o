#!/usr/bin/env python
#
# Any copyright is dedicated to the Public Domain.
# http://creativecommons.org/publicdomain/zero/1.0/
#
# Test that some symbol server requests work. Run this script with
# a URL as the first commandline argument to point it at a different instance.

# NOTE: be sure to only use symbols that aren't going to get removed from
# the symbol server. The URLs in use here are all from Firefox 18.0.2.

import sys
import unittest
import urllib2
import urlparse


class TestSymbolServer(unittest.TestCase):
    SERVER = 'http://symbols.mozilla.org/'

    def check(self, url, first_line=None):
        full_url = urlparse.urljoin(self.SERVER, url)
        req = urllib2.Request(full_url)
        if first_line is None:
            # Do a HEAD if we don't care about the data.
            req.get_method = lambda: 'HEAD'
        res = urllib2.urlopen(req)
        # If we ever make symbols.mo return redirects instead of proxying,
        # this will have to change. Maybe just require `requests`.
        self.assertEqual(res.getcode(), 200)
        if first_line is not None:
            self.assertEqual(res.readline().rstrip(), first_line)

    def test_basic(self):
        self.check('/firefox.pdb/448794C699914DB8A8F9B9F88B98D7412/firefox.sym',
                   'MODULE windows x86 448794C699914DB8A8F9B9F88B98D7412 firefox.pdb')

    # Just for sanity, make sure that requests for native debug symbols work
    # for Windows/Linux/Mac symbols.
    def test_basic_pdb(self):
        self.check('/firefox.pdb/448794C699914DB8A8F9B9F88B98D7412/firefox.pd_')

    def test_basic_dbg(self):
        self.check('libxul.so/20BC1801B0B1864324D3B9E933328A170/libxul.so.dbg.gz')

    def test_basic_dsym(self):
        self.check('XUL/E3532A114F1C37E2AF567D8E6975F80C0/XUL.dSYM.tar.bz2')

    def test_mixed_case(self):
        'bug 660932, bug 414852'
        self.check('/firefox.pdb/448794c699914db8a8f9b9f88b98d7412/firefox.sym',
                   'MODULE windows x86 448794C699914DB8A8F9B9F88B98D7412 firefox.pdb')

    def test_old_firefox_prefix(self):
        self.check('/firefox/firefox.pdb/448794C699914DB8A8F9B9F88B98D7412/firefox.sym',
                   'MODULE windows x86 448794C699914DB8A8F9B9F88B98D7412 firefox.pdb')

    def test_old_thunderbird_prefix(self):
        # Yes, this looks dumb.
        self.check('/thunderbird/firefox.pdb/448794C699914DB8A8F9B9F88B98D7412/firefox.sym',
                   'MODULE windows x86 448794C699914DB8A8F9B9F88B98D7412 firefox.pdb')

    def test_firefox_without_prefix(self):
        '''
        bug 1246151 - The firefox binary on Linux/Mac is just named `firefox`,
        so make sure the rewrite rules to strip the app name don't
        break downloading these files.
        '''
        self.check('/firefox/946C0C63132015DD88CA2EFCBB9AC4C70/firefox.sym',
                   'MODULE Linux x86_64 946C0C63132015DD88CA2EFCBB9AC4C70 firefox')

    def test_firefox_without_prefix(self):
        '''
        bug 1246151 - The firefox binary on Linux/Mac is just named `firefox`,
        so make sure the rewrite rules to strip the app name don't
        break downloading these files.
        '''
        self.check('/firefox/946C0C63132015DD88CA2EFCBB9AC4C70/firefox.sym',
                   'MODULE Linux x86_64 946C0C63132015DD88CA2EFCBB9AC4C70 firefox')

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1].startswith('http'):
        TestSymbolServer.SERVER = sys.argv.pop(1)
    unittest.main()
