"""Guard test for the endpoint naming rule, batch 12 task 3.

The P3 trap: port 9223 is two browsers. 127.0.0.1:9223 is Chromium
(clone2), [::1]:9223 is Brave (clone1). A harness that resolves an
endpoint from a bare port, from 'localhost', or from a host plus
port with no browser name silently drives the wrong browser. The
guard fails any resolver that accepts such a spec.

The test has three parts:
1. TestCorrectResolver / TestParseEndpointRef: the rule in
   scripts/endpoint_names.py accepts exactly the fully-qualified
   specs and rejects every ambiguous one.
2. TestNaiveResolverTrap: the old behavior, scripts/endpoint_names.py
   naive_resolve(), is run against the same specs to show what it
   does wrong: a Brave intent resolves to the Chromium endpoint,
   and 'localhost' resolves to 127.0.0.1 while this machine's
   resolver returns ::1 first. These tests pass by exposing the
   trap; they are the failing-first evidence in test form.
3. TestGuardCatchesNaive: the guard assertions themselves are run
   against the naive resolver, and the test asserts the naive
   resolver lets every ambiguous spec through, i.e. the guard
   would fail a harness wired to it.

Standalone: no browser, no network listener, no SSH. Pure stdlib.
Run: python3 -m unittest tests.test_endpoint_naming_guard -v
(or from tests/: python3 -m unittest test_endpoint_naming_guard -v)
"""
import socket
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))

from endpoint_names import (  # noqa: E402
    EndpointAmbiguityError,
    KNOWN_ENDPOINTS,
    naive_resolve,
    parse_endpoint_ref,
    resolve_endpoint,
)

BRAVE_URL = 'http://[::1]:9223'
CHROMIUM_URL = 'http://127.0.0.1:9223'


class TestCorrectResolver(unittest.TestCase):
    def test_brave_resolves_to_ipv6_loopback(self):
        self.assertEqual(
            resolve_endpoint('brave', '::1', 9223, 'clone1'), BRAVE_URL)

    def test_chromium_resolves_to_ipv4_loopback(self):
        self.assertEqual(
            resolve_endpoint('chromium', '127.0.0.1', 9223, 'clone2'),
            CHROMIUM_URL)

    def test_same_port_two_browsers_are_different_endpoints(self):
        self.assertNotEqual(
            resolve_endpoint('brave', '::1', 9223, 'clone1'),
            resolve_endpoint('chromium', '127.0.0.1', 9223, 'clone2'))

    def test_missing_browser_is_rejected(self):
        for bad in (None, '', 9223):
            with self.assertRaises(EndpointAmbiguityError):
                resolve_endpoint(bad, '::1', 9223, 'clone1')

    def test_unknown_browser_is_rejected(self):
        with self.assertRaises(EndpointAmbiguityError):
            resolve_endpoint('zen', '127.0.0.1', 9223, 'clone1')

    def test_localhost_host_is_rejected(self):
        for browser, host, owner in (('brave', 'localhost', 'clone1'),
                                     ('chromium', 'localhost', 'clone2')):
            with self.assertRaises(EndpointAmbiguityError):
                resolve_endpoint(browser, host, 9223, owner)

    def test_uppercase_localhost_gets_the_localhost_message(self):
        with self.assertRaisesRegex(EndpointAmbiguityError, 'localhost'):
            resolve_endpoint('brave', 'LOCALHOST', 9223, 'clone1')

    def test_swapped_loopback_family_is_rejected(self):
        # The P3 trap in spec form: brave on IPv4 is Chromium, and
        # chromium on IPv6 is Brave. Both must refuse, not repair.
        with self.assertRaises(EndpointAmbiguityError):
            resolve_endpoint('brave', '127.0.0.1', 9223, 'clone1')
        with self.assertRaises(EndpointAmbiguityError):
            resolve_endpoint('chromium', '::1', 9223, 'clone2')

    def test_missing_host_is_rejected(self):
        for bad in (None, ''):
            with self.assertRaises(EndpointAmbiguityError):
                resolve_endpoint('brave', bad, 9223, 'clone1')

    def test_missing_port_is_rejected_no_silent_default(self):
        for bad in (None, '9223'):
            with self.assertRaises(EndpointAmbiguityError):
                resolve_endpoint('brave', '::1', bad, 'clone1')

    def test_wrong_port_is_rejected(self):
        with self.assertRaises(EndpointAmbiguityError):
            resolve_endpoint('brave', '::1', 9224, 'clone1')
        with self.assertRaises(EndpointAmbiguityError):
            resolve_endpoint('chromium', '127.0.0.1', 9222, 'clone2')

    def test_bad_port_range_is_rejected(self):
        for bad in (0, 65536, -1):
            with self.assertRaises(EndpointAmbiguityError):
                resolve_endpoint('brave', '::1', bad, 'clone1')

    def test_non_loopback_host_is_rejected(self):
        with self.assertRaises(EndpointAmbiguityError):
            resolve_endpoint('brave', '192.168.1.13', 9223, 'clone1')

    def test_missing_owner_is_rejected(self):
        for bad in (None, ''):
            with self.assertRaises(EndpointAmbiguityError):
                resolve_endpoint('brave', '::1', 9223, bad)

    def test_owner_mismatch_is_rejected(self):
        with self.assertRaises(EndpointAmbiguityError):
            resolve_endpoint('brave', '::1', 9223, 'clone2')
        with self.assertRaises(EndpointAmbiguityError):
            resolve_endpoint('chromium', '127.0.0.1', 9223, 'clone1')

    def test_registry_covers_both_live_browsers(self):
        self.assertEqual(set(KNOWN_ENDPOINTS), {'brave', 'chromium'})
        for row in KNOWN_ENDPOINTS.values():
            self.assertIn(row['host'], ('127.0.0.1', '::1'))
            self.assertEqual(row['port'], 9223)


class TestParseEndpointRef(unittest.TestCase):
    def test_bare_port_is_rejected(self):
        for bad in ('9223', ':9223', '9223/clone1'):
            with self.assertRaises(EndpointAmbiguityError):
                parse_endpoint_ref(bad, 'brave')

    def test_localhost_forms_are_rejected(self):
        for bad in ('localhost:9223', 'http://localhost:9223',
                    'http://localhost', 'localhost'):
            with self.assertRaises(EndpointAmbiguityError):
                parse_endpoint_ref(bad, 'brave')

    def test_url_without_port_is_rejected(self):
        with self.assertRaises(EndpointAmbiguityError):
            parse_endpoint_ref('http://[::1]', 'brave')
        with self.assertRaises(EndpointAmbiguityError):
            parse_endpoint_ref('http://127.0.0.1', 'chromium')

    def test_url_without_browser_context_is_rejected(self):
        # A URL alone does not name a browser: no browser, no resolve.
        with self.assertRaises(EndpointAmbiguityError):
            parse_endpoint_ref('http://[::1]:9223', None)
        with self.assertRaises(EndpointAmbiguityError):
            parse_endpoint_ref('http://127.0.0.1:9223', '')

    def test_swapped_family_url_is_rejected(self):
        with self.assertRaises(EndpointAmbiguityError):
            parse_endpoint_ref('http://127.0.0.1:9223', 'brave')
        with self.assertRaises(EndpointAmbiguityError):
            parse_endpoint_ref('http://[::1]:9223', 'chromium')

    def test_non_http_scheme_is_rejected(self):
        with self.assertRaises(EndpointAmbiguityError):
            parse_endpoint_ref('ws://[::1]:9223', 'brave')

    def test_userinfo_is_rejected(self):
        for bad in ('http://user:pass@[::1]:9223',
                    'http://user@[::1]:9223'):
            with self.assertRaises(EndpointAmbiguityError):
                parse_endpoint_ref(bad, 'brave')

    def test_path_query_fragment_are_rejected(self):
        for bad in ('http://[::1]:9223/', 'http://[::1]:9223/json/list',
                    'http://[::1]:9223?x=1', 'http://[::1]:9223#frag'):
            with self.assertRaises(EndpointAmbiguityError):
                parse_endpoint_ref(bad, 'brave')

    def test_unhashable_browser_raises_ambiguity_not_type_error(self):
        with self.assertRaises(EndpointAmbiguityError):
            parse_endpoint_ref('http://[::1]:9223', ['brave'])
        with self.assertRaises(EndpointAmbiguityError):
            parse_endpoint_ref('http://[::1]:9223', {'brave': 1})

    def test_out_of_range_port_says_out_of_range(self):
        with self.assertRaisesRegex(EndpointAmbiguityError,
                                    'out of range'):
            parse_endpoint_ref('http://127.0.0.1:99999', 'chromium')

    def test_non_numeric_port_says_not_a_number(self):
        with self.assertRaisesRegex(EndpointAmbiguityError,
                                    'not a number'):
            parse_endpoint_ref('http://127.0.0.1:abc', 'chromium')

    def test_non_loopback_url_is_rejected(self):
        with self.assertRaises(EndpointAmbiguityError):
            parse_endpoint_ref('http://192.168.1.13:9223', 'brave')

    def test_fully_qualified_refs_resolve(self):
        self.assertEqual(
            parse_endpoint_ref('http://[::1]:9223', 'brave'), BRAVE_URL)
        self.assertEqual(
            parse_endpoint_ref('http://127.0.0.1:9223', 'chromium'),
            CHROMIUM_URL)


class TestNaiveResolverTrap(unittest.TestCase):
    """Failing-first evidence: the old behavior misroutes."""

    def test_bare_port_brave_intent_lands_on_chromium(self):
        # Pre-fix, a program aimed at Brave by bare port 9223 drove
        # the default 127.0.0.1:9223, which is Chromium, not Brave.
        got = naive_resolve('9223', browser='brave')
        self.assertEqual(got, CHROMIUM_URL)
        self.assertNotEqual(got, BRAVE_URL)

    def test_localhost_answer_depends_on_the_resolver(self):
        # Order-independent: localhost maps to two families on every
        # machine (both answers are present here), and the naive
        # resolver picks one of them. On a machine with IPv4-first
        # resolution the naive answer would coincide with the OS
        # answer by luck, which is exactly why localhost must be
        # banned rather than resolved: the answer depends on the
        # resolver, not on the reference.
        answers = {a[4][0] for a in socket.getaddrinfo(
            'localhost', 9223, 0, socket.SOCK_STREAM)}
        self.assertIn('::1', answers)
        self.assertIn('127.0.0.1', answers)
        got = naive_resolve('localhost:9223')
        self.assertEqual(got, 'http://127.0.0.1:9223')
        self.assertNotEqual(got, 'http://[::1]:9223')

    def test_naive_ignores_the_browser_name(self):
        self.assertEqual(naive_resolve('9223', browser='brave'),
                         naive_resolve('9223', browser='chromium'))

    def test_naive_accepts_a_missing_port(self):
        self.assertEqual(naive_resolve('http://[::1]', browser='brave'),
                         'http://[::1]:9223')


class TestGuardCatchesNaive(unittest.TestCase):
    """The guard would fail a harness wired to the naive resolver."""

    AMBIGUOUS_SPECS = [
        ('9223', 'brave'),
        (':9223', 'brave'),
        ('localhost:9223', 'brave'),
        ('http://localhost:9223', 'brave'),
        ('http://localhost:9223', 'chromium'),
        ('http://127.0.0.1', 'chromium'),
        ('http://[::1]', 'brave'),
        ('http://127.0.0.1:9223', 'brave'),
        ('http://[::1]:9223', 'chromium'),
    ]

    def test_guard_rejects_every_ambiguous_spec(self):
        for text, browser in self.AMBIGUOUS_SPECS:
            with self.assertRaises(EndpointAmbiguityError, msg=text):
                parse_endpoint_ref(text, browser)

    def test_naive_lets_every_ambiguous_spec_through(self):
        # If any of these raised, the naive resolver would already
        # be guarded. It lets all 9 through, so the guard is what
        # stands between a bare '9223' and the wrong browser.
        let_through = 0
        for text, browser in self.AMBIGUOUS_SPECS:
            try:
                naive_resolve(text, browser=browser)
                let_through += 1
            except EndpointAmbiguityError:
                pass
        self.assertEqual(let_through, len(self.AMBIGUOUS_SPECS))


if __name__ == '__main__':
    unittest.main()
