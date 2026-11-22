"""Endpoint naming rule, batch 12 task 3 (P3 port split follow-up).

An endpoint reference names a browser. A bare port never does: port
9223 is two different browsers on the laptop, Chromium on
127.0.0.1 and Brave on [::1], and a run that assumes "port 9223 is
Brave" silently drives the wrong browser. The hostname "localhost"
names no browser either: it maps to both loopback families, and
which one a client reaches first depends on the resolver. On this
VM socket.getaddrinfo('localhost', 9223) returns ::1 first, then
127.0.0.1, so a client connecting to localhost:9223 reaches Brave,
not the 127.0.0.1 default. Any resolver that accepts localhost or a
bare port is guessing, and the guess is wrong half the time.

Every endpoint reference carries four fields, all required:
  browser: a registry key, e.g. 'brave' or 'chromium'
  host: an IP literal, '127.0.0.1' or '::1', never 'localhost'
  port: an integer 1..65535, always written out, never defaulted
  owner: the chat or purpose the browser serves, e.g. 'clone1'

resolve_endpoint() returns the canonical CDP URL string, e.g.
'http://[::1]:9223'. It raises EndpointAmbiguityError (a ValueError)
on any ambiguous, incomplete, or registry-mismatched spec instead
of guessing. parse_endpoint_ref() does the same for a free-form
reference string: a string that does not carry a browser name can
never resolve, because host plus port alone do not name a browser.

The registry is the single source of truth for which browser lives
where. Adding a browser means registering it here first, with ss
plus /json/version evidence, never by editing a call site to use a
bare port. This module is pure stdlib and has no dependency on cu.py
or cdp.mjs, so the guard test can run anywhere without a browser.

Evidence for the registry (see docs/clone2-endpoint-naming-rule-20261122.md):
  Brave [::1]:9223, clone1: P3 probe log improvements/worker-click4-p3-probe-log.md
    section 2.5, ss output and /json/version Chrome/157.0.8103.79.
  Chromium 127.0.0.1:9223, clone2: same log, /json/version
    Chrome/157.0.8103.38, Chromium PID 8059 since Nov 21.
"""

# Registry: browser key -> the only host, port and owner that may be
# used for it. A spec that disagrees with its row is rejected, not
# repaired: the disagreement is the P3 trap in spec form.
KNOWN_ENDPOINTS = {
    'brave': {'host': '::1', 'port': 9223, 'owner': 'clone1',
              'kind': 'Brave'},
    'chromium': {'host': '127.0.0.1', 'port': 9223, 'owner': 'clone2',
                 'kind': 'Chromium'},
}


class EndpointAmbiguityError(ValueError):
    """An endpoint reference does not name exactly one browser."""


def _canonical_url(host, port):
    if ':' in host:
        return 'http://[%s]:%d' % (host, port)
    return 'http://%s:%d' % (host, port)


def resolve_endpoint(browser, host, port, owner):
    """Resolve a four-field spec to its canonical CDP URL.

    Raises EndpointAmbiguityError when any field is missing, when the
    browser is unknown, when the host is not an IP literal, when the
    port is missing or out of range, or when any field disagrees with
    the registry row for that browser. The port is never defaulted:
    a missing port is an error, because the old silent default (9223)
    is exactly the port two browsers share.
    """
    if not isinstance(browser, str) or not browser:
        raise EndpointAmbiguityError('browser name is required')
    row = KNOWN_ENDPOINTS.get(browser)
    if row is None:
        raise EndpointAmbiguityError(
            'unknown browser %r: register it first, with ss plus '
            '/json/version evidence' % (browser,))
    if not isinstance(host, str) or not host:
        raise EndpointAmbiguityError('host literal is required')
    if host.lower() == 'localhost':
        raise EndpointAmbiguityError(
            'localhost is ambiguous: it maps to both 127.0.0.1 and '
            '::1, so it names no single browser')
    if host != row['host']:
        raise EndpointAmbiguityError(
            'host %r does not match %s (%s): the P3 trap, host and '
            'browser disagree' % (host, browser, row['host']))
    if isinstance(port, bool) or not isinstance(port, int):
        raise EndpointAmbiguityError('port is required as an integer')
    if not 1 <= port <= 65535:
        raise EndpointAmbiguityError('port must be 1..65535')
    if port != row['port']:
        raise EndpointAmbiguityError(
            'port %d does not match %s (%d)' % (port, browser, row['port']))
    if not isinstance(owner, str) or not owner:
        raise EndpointAmbiguityError('owner is required')
    if owner != row['owner']:
        raise EndpointAmbiguityError(
            'owner %r does not match %s (%s)' % (owner, browser, row['owner']))
    return _canonical_url(host, port)


def parse_endpoint_ref(text, browser):
    """Resolve a free-form endpoint reference for one named browser.

    The reference must be a full http URL with an explicit IP-literal
    host and an explicit port, and nothing else: no userinfo, no path,
    no query, no fragment. Anything less, or anything more, is
    rejected: a bare port ('9223'), a host without a scheme,
    'localhost' in any form, a URL without a port, and a URL carrying
    credentials or a path. The browser argument is required because a
    URL alone does not name a browser; the parsed host and port are
    checked against the registry row for that browser. The browser
    is validated before any registry lookup, so an unhashable browser
    raises EndpointAmbiguityError like every other bad spec.
    """
    if not isinstance(text, str) or not text.strip():
        raise EndpointAmbiguityError('endpoint reference is required')
    if not isinstance(browser, str) or browser not in KNOWN_ENDPOINTS:
        raise EndpointAmbiguityError(
            'browser name is required and must be a known browser: '
            'register it first, with ss plus /json/version evidence')
    text = text.strip()
    if '://' not in text:
        raise EndpointAmbiguityError(
            'endpoint reference %r has no scheme: a bare port or a '
            'bare host never names a browser' % (text,))
    import urllib.parse
    url = urllib.parse.urlparse(text)
    if url.scheme != 'http':
        raise EndpointAmbiguityError(
            'endpoint scheme must be http, got %r' % (url.scheme,))
    if url.username is not None or url.password is not None:
        raise EndpointAmbiguityError(
            'endpoint reference %r carries credentials: an endpoint '
            'reference is a bare host and port, never a login' % (text,))
    if url.path not in ('',):
        raise EndpointAmbiguityError(
            'endpoint reference %r carries a path: an endpoint '
            'reference is a bare host and port' % (text,))
    if url.query:
        raise EndpointAmbiguityError(
            'endpoint reference %r carries a query: an endpoint '
            'reference is a bare host and port' % (text,))
    if url.fragment:
        raise EndpointAmbiguityError(
            'endpoint reference %r carries a fragment: an endpoint '
            'reference is a bare host and port' % (text,))
    if not url.hostname:
        raise EndpointAmbiguityError(
            'endpoint reference %r has no host' % (text,))
    if url.hostname == 'localhost':
        raise EndpointAmbiguityError(
            'localhost is ambiguous: it maps to both 127.0.0.1 and '
            '::1, so it names no single browser')
    port = _port_from_url(url, text)
    return resolve_endpoint(browser, url.hostname, port,
                            KNOWN_ENDPOINTS[browser]['owner'])


def _port_from_url(url, text):
    """Extract the port from a parsed URL, with an exact error.

    url.port raises one ValueError for both a non-numeric port and
    an out-of-range port; this separates the two so the message
    states which one it is. A missing port is its own error: no
    silent default, 9223 is two browsers.
    """
    import re
    netloc = url.netloc
    if netloc.startswith('['):
        rest = netloc.split(']:', 1)
        port_text = rest[1] if len(rest) == 2 else None
    else:
        port_text = netloc.rsplit(':', 1)[1] if ':' in netloc else None
    if port_text is None or port_text == '':
        raise EndpointAmbiguityError(
            'endpoint port is required: no silent default, 9223 is '
            'two browsers')
    if not re.fullmatch(r'[0-9]+', port_text):
        raise EndpointAmbiguityError(
            'endpoint port is not a number: %r' % (port_text,))
    port = int(port_text)
    if not 1 <= port <= 65535:
        raise EndpointAmbiguityError(
            'endpoint port out of range: %d' % (port,))
    return port


def naive_resolve(text, browser=None):
    """The OLD defaults, kept only to demonstrate the trap.

    This mimics the pre-fix defaults: a bare port or a missing host
    defaults to 127.0.0.1:9223, a missing port defaults to 9223, and
    the browser name is ignored. DO NOT USE: for a Brave intent it
    returns the Chromium endpoint.

    One leg is NOT the old behavior and is labelled as such: the
    localhost leg. The real pre-fix stack passed a localhost
    endpoint unchanged to cdp.mjs, whose fetch resolves it through
    the OS (::1 first on this VM, i.e. Brave), so the old stack's
    real localhost answer was Brave, not Chromium. This function
    instead rewrites bare 'localhost:9223' to 127.0.0.1:9223, which
    models a hypothetical hardcoding resolver, not the old stack.
    The rule (localhost is ambiguous) does not depend on which
    answer is right: the OS resolver and a hardcoded default can
    disagree, and both real clients fall back to the other family
    when the first refuses, so localhost means "whichever browser
    is up", not one browser. See docs/clone2-endpoint-naming-rule-20261122.md
    section 3 for the live experiment.
    """
    import urllib.parse
    if text is None:
        text = ''
    text = str(text).strip()
    if not text:
        return 'http://127.0.0.1:9223'
    if '://' not in text:
        if text.isdigit():
            return 'http://127.0.0.1:%d' % int(text)
        return 'http://127.0.0.1:9223'
    url = urllib.parse.urlparse(text)
    host = url.hostname or '127.0.0.1'
    try:
        port = url.port or 9223
    except ValueError:
        port = 9223
    if ':' in host:
        return 'http://[%s]:%d' % (host, port)
    return 'http://%s:%d' % (host, port)
