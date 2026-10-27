#!/usr/bin/env python3
"""Private byte-level transport used by scripts/mcp_bridge.py.

Ownership model (regression guard for the OSError 9 defect):
- The bridge session OWNS the driver child process and every stdio stream.
- The objects here BORROW a live stream object and retain the reference for
  their whole life; they never close a stream and never retain a bare
  integer fd. The previous implementation kept only the integer fd of a
  temporary ``os.fdopen()`` wrapper; the wrapper was garbage-collected and
  closed the fd in the middle of a session. Closing and reaping happen
  exactly once, in the bridge's ``close_session()``.

Framing model:
- Every read on the driver's stdout is an incremental raw byte read on the
  SAME stream object; buffered readline is never mixed with raw reads on
  the same stdout. The stream must therefore be a raw binary stream
  (``subprocess.Popen(..., bufsize=0)`` yields ``io.FileIO``) or a test
  double whose ``read(n)`` may return fewer bytes than requested.
- Bytes are accumulated and UTF-8 is decoded only after a complete
  newline-terminated line has been assembled; bytes that arrive after a
  newline are retained for the next line.
- A line is capped at ``DEFAULT_MAX_LINE_BYTES`` (32 MiB, newline excluded):
  a line of exactly the cap is accepted, cap+1 is refused.
- Deadlines are monotonic and injectable (constructor timeout, per-call
  absolute ``deadline`` for read_line).

Write model:
- ``write_request`` bounds request WRITES with the same nonblocking
  write/select/deadline pattern as ``scripts/browser_worker.py`` (no new
  dependency): the fd is switched to nonblocking, written in chunks under
  ``select`` polling, and a partial write past the deadline raises
  WriteTimeoutError with the exact byte count already sent.
"""
import json
import math
import os
import select
import time

DEFAULT_STARTUP_TIMEOUT = 60.0
DEFAULT_REQUEST_TIMEOUT = 90.0
DEFAULT_MAX_LINE_BYTES = 32 * 1024 * 1024
READ_CHUNK_SIZE = 65536
WRITE_CHUNK_SIZE = 65536
POLL_SECONDS = 0.04


class TransportError(Exception):
    """Base class for transport failures; str(exc) is a truthful reason."""


class ResponseTimeoutError(TransportError):
    """No complete line arrived before the monotonic deadline."""


class WriteTimeoutError(TransportError):
    """The request could not be fully written before the deadline."""


class LineTooLongError(TransportError):
    """A line exceeded the configured byte cap."""


class StreamClosedError(TransportError):
    """The stream reached EOF; partial_bytes counts undelivered mid-line bytes."""

    def __init__(self, message, partial_bytes=0):
        super().__init__(message)
        self.partial_bytes = partial_bytes


class MessageError(TransportError):
    """A complete line was received but is not a UTF-8 JSON object."""


def _fd_of(stream):
    """Return the stream's real fd, or None for fd-less test doubles."""
    try:
        fd = stream.fileno()
    except (AttributeError, OSError, ValueError):
        return None
    if fd is None or fd < 0:
        return None
    return fd


def wait_readable(stream, timeout):
    """True when the stream has bytes ready (or is an fd-less test double
    whose reads are scripted and need no polling)."""
    fd = _fd_of(stream)
    if fd is None:
        return True
    ready, _, _ = select.select([fd], [], [], timeout)
    return bool(ready)


class LineReader:
    """Assembles newline-terminated lines from incremental raw byte reads.

    The stream is borrowed, never owned: the reader keeps the object
    reference alive for its whole life and never closes it, so the owning
    session decides the single close/teardown moment.
    """

    def __init__(self, stream, timeout=DEFAULT_REQUEST_TIMEOUT,
                 max_line_bytes=DEFAULT_MAX_LINE_BYTES):
        timeout = float(timeout)
        max_line_bytes = int(max_line_bytes)
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        if max_line_bytes <= 0:
            raise ValueError("max_line_bytes must be positive")
        self._stream = stream
        self._timeout = timeout
        self._max_line_bytes = max_line_bytes
        self._pending = bytearray()

    @property
    def stream(self):
        """The borrowed live stream object (retained for the reader's life)."""
        return self._stream

    @property
    def timeout(self):
        return self._timeout

    @property
    def max_line_bytes(self):
        return self._max_line_bytes

    @property
    def pending_bytes(self):
        """Bytes received after the last complete line, waiting for a newline."""
        return len(self._pending)

    def read_line(self, deadline=None):
        """Return the next line WITHOUT the trailing newline as bytes.

        Blocks with a monotonic total deadline (absolute ``deadline`` or
        ``now + self.timeout``). Raises ResponseTimeoutError on deadline,
        LineTooLongError over the cap, StreamClosedError at EOF (with
        partial_bytes set when EOF cut a line in half).
        """
        if deadline is None:
            deadline = time.monotonic() + self._timeout
        while True:
            cut = self._pending.find(b"\n")
            if cut >= 0:
                if cut > self._max_line_bytes:
                    # Consume (discard) the whole oversized line, newline
                    # included, so the stream stays frame-consistent.
                    del self._pending[:cut + 1]
                    raise LineTooLongError(
                        "line exceeds the %d byte cap (%d bytes)"
                        % (self._max_line_bytes, cut))
                line = bytes(self._pending[:cut])
                del self._pending[:cut + 1]
                return line
            if len(self._pending) > self._max_line_bytes:
                raise LineTooLongError(
                    "line exceeds the %d byte cap (%d bytes buffered without a newline)"
                    % (self._max_line_bytes, len(self._pending)))
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise ResponseTimeoutError(
                    "no complete line before the deadline; %d byte(s) buffered without a newline"
                    % len(self._pending))
            if not wait_readable(self._stream, remaining):
                continue  # poll slice elapsed; re-check the deadline first
            chunk = self._stream.read(READ_CHUNK_SIZE)
            if chunk is None:
                # Non-blocking race: nothing ready after all; brief sleep, re-check.
                time.sleep(min(POLL_SECONDS, max(remaining, 0.0)))
                continue
            if not chunk:
                if self._pending:
                    raise StreamClosedError(
                        "stream closed mid-line with %d undelivered byte(s)"
                        % len(self._pending), partial_bytes=len(self._pending))
                raise StreamClosedError(
                    "stream closed before a complete line arrived", 0)
            self._pending.extend(chunk)


def _reject_parse_constant(name):
    """Reject the nonstandard JSON constants json accepts by default."""
    raise ValueError("nonstandard JSON constant: %s" % name)


def _parse_finite_float(text):
    """Parse a JSON number that must stay a finite float.

    Rejects exponents that decode to inf/nan (e.g. 1e999) so a non-finite
    value can never slip into the MCP payload and be re-serialized as
    Infinity (which is not standard JSON).
    """
    value = float(text)
    if not math.isfinite(value):
        raise ValueError("non-finite number in response: %s" % text)
    return value


def decode_message(line):
    """Decode one complete line into a JSON object envelope.

    UTF-8 is decoded only here, after the line is complete. Raises
    MessageError (truthful reason) for invalid UTF-8, invalid JSON, a
    non-object envelope, or any non-finite/nonstandard numeric constant
    (NaN / ±Infinity literals and overflow exponents); the caller must
    treat that as a failed response, never consume or replay it. Finite
    numbers, Unicode strings and plain object envelopes decode normally.
    """
    try:
        text = line.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise MessageError("response is not valid UTF-8: %s" % exc) from exc
    try:
        value = json.loads(text, parse_constant=_reject_parse_constant,
                           parse_float=_parse_finite_float)
    except ValueError as exc:
        raise MessageError("response is not valid JSON: %s" % exc) from exc
    if not isinstance(value, dict):
        raise MessageError("response envelope is not a JSON object (got %s)"
                           % type(value).__name__)
    return value


def write_request(stream, payload, deadline):
    """Write the whole request payload before the monotonic deadline.

    Borrows the live stdin stream (never closes it). For fd-backed streams
    this is the scripts/browser_worker.py pattern: switch the fd to
    nonblocking (idempotent), then chunk os.write under select polling so a
    stalled child can never block the bridge past the deadline. A partial
    write raises WriteTimeoutError reporting how many bytes were already
    sent — the caller must treat the outcome as uncertain and never resend.
    Fd-less test doubles get a single direct write before the deadline.
    """
    payload = memoryview(payload)
    total = len(payload)
    fd = _fd_of(stream)
    if fd is None:
        if time.monotonic() >= deadline:
            raise WriteTimeoutError(
                "request write deadline already passed (0 of %d bytes sent)"
                % total)
        stream.write(bytes(payload))
        stream.flush()
        return
    os.set_blocking(fd, False)
    sent = 0
    while sent < total:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise WriteTimeoutError(
                "request write did not finish within the deadline (%d of %d bytes sent)"
                % (sent, total))
        if not select.select([], [fd], [], min(remaining, POLL_SECONDS))[1]:
            continue  # poll slice elapsed; re-check the deadline first
        try:
            sent += os.write(fd, payload[sent:sent + WRITE_CHUNK_SIZE])
        except BlockingIOError:
            continue  # writability raced away; poll again
    if sent != total:  # pragma: no cover - os.write never returns 0 on a pipe
        raise WriteTimeoutError(
            "request write stopped early (%d of %d bytes sent)" % (sent, total))
