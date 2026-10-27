"""GUI-free tests for scripts/mcp_bridge_transport.py.

Only owned pipes (os.pipe pairs closed via addCleanup) and scripted fake
streams are used: no real child processes, no desktop, no sockets, no
installed bridge, no global state. Deadlines and caps are injected short
values; nothing here relies on timing guesses beyond generous bounds.
"""
import gc
import io
import json
import os
import sys
import time
import unittest
from pathlib import Path

TREE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TREE_ROOT / "scripts"))
import mcp_bridge_transport as transport


class ScriptedStream:
    """Fd-less fake whose read() replays a fixed sequence of deliveries.

    Each read() call consumes exactly one scripted chunk, so tests assert
    on ACTUAL separate read() deliveries, not on kernel buffering luck.
    """

    def __init__(self, chunks):
        self.chunks = list(chunks)
        self.read_calls = 0
        self.read_sizes = []
        self.closed = False
        self.writes = []

    def fileno(self):
        raise io.UnsupportedOperation("scripted stream has no fd")

    def read(self, size):
        self.read_calls += 1
        self.read_sizes.append(size)
        if self.chunks:
            return self.chunks.pop(0)
        return b""  # EOF once the script is exhausted

    def write(self, data):
        self.writes.append(bytes(data))
        return len(data)

    def flush(self):
        pass

    def close(self):
        self.closed = True


class OwnedPipe:
    """An os.pipe pair wrapped as raw binary streams; addCleanup everything."""

    def __init__(self, testcase):
        read_fd, write_fd = os.pipe()
        self.reader = os.fdopen(read_fd, "rb", buffering=0)
        self.writer = os.fdopen(write_fd, "wb", buffering=0)
        testcase.addCleanup(self.close)

    def close(self):
        for name in ("reader", "writer"):
            stream = getattr(self, name, None)
            try:
                if stream and not stream.closed:
                    stream.close()
            except (OSError, ValueError):
                pass

    def write(self, data):
        self.writer.write(data)
        self.writer.flush()


class LineReadingTests(unittest.TestCase):
    def setUp(self):
        self.pipe = None

    def make_reader(self, chunks=None, timeout=5.0, max_line_bytes=None):
        if chunks is None:
            self.pipe = OwnedPipe(self)
            stream = self.pipe.reader
        else:
            stream = ScriptedStream(chunks)
        kwargs = {"timeout": timeout}
        if max_line_bytes is not None:
            kwargs["max_line_bytes"] = max_line_bytes
        reader = transport.LineReader(stream, **kwargs)
        self.addCleanup(self.close_stream, stream)
        return reader, stream

    def close_stream(self, stream):
        try:
            if not stream.closed:
                stream.close()
        except (OSError, ValueError):
            pass

    def test_ordinary_line_and_object_envelope(self):
        reader, stream = self.make_reader()
        self.pipe.write(b'{"driver": "ready"}\n')
        line = reader.read_line()
        self.assertEqual(line, b'{"driver": "ready"}')
        self.assertEqual(transport.decode_message(line), {"driver": "ready"})
        self.assertEqual(reader.pending_bytes, 0)
        self.assertFalse(stream.closed, "reader must not close a borrowed stream")

    def test_two_complete_lines_in_one_read_chunk(self):
        reader, _ = self.make_reader()
        self.pipe.write(b'{"a": 1}\n{"b": 2}\n')
        self.assertEqual(reader.read_line(), b'{"a": 1}')
        self.assertEqual(reader.read_line(), b'{"b": 2}')
        self.assertEqual(reader.pending_bytes, 0)

    def test_bytes_after_newline_are_retained_for_next_line(self):
        reader, _ = self.make_reader()
        self.pipe.write(b'{"first": true}\n{"sec')
        self.assertEqual(reader.read_line(), b'{"first": true}')
        self.assertEqual(reader.pending_bytes, len(b'{"sec'))
        self.pipe.write(b'ond": 1}\n')
        self.assertEqual(reader.read_line(), b'{"second": 1}')

    def test_partial_line_then_stall_until_deadline(self):
        reader, _ = self.make_reader(timeout=0.4)
        self.pipe.write(b'{"partial":')
        started = time.monotonic()
        with self.assertRaises(transport.ResponseTimeoutError) as caught:
            reader.read_line()
        elapsed = time.monotonic() - started
        self.assertGreaterEqual(elapsed, 0.3)
        self.assertLess(elapsed, 5.0)
        self.assertEqual(reader.pending_bytes, len(b'{"partial":'))
        self.assertIn("buffered", str(caught.exception))

    def test_empty_eof(self):
        reader, _ = self.make_reader()
        self.pipe.writer.close()
        with self.assertRaises(transport.StreamClosedError) as caught:
            reader.read_line()
        self.assertEqual(caught.exception.partial_bytes, 0)
        self.assertIn("before", str(caught.exception))

    def test_eof_midline(self):
        reader, _ = self.make_reader()
        self.pipe.write(b'{"returnc')
        self.pipe.writer.close()
        with self.assertRaises(transport.StreamClosedError) as caught:
            reader.read_line()
        self.assertEqual(caught.exception.partial_bytes, len(b'{"returnc'))
        self.assertIn("mid-line", str(caught.exception))

    def test_line_split_across_deliveries_is_assembled(self):
        # Pins the original partial-line bug: a line delivered through
        # several read() calls must be assembled whole, and bytes after a
        # newline must survive into the next line.
        reader, stream = self.make_reader(
            chunks=[b'{"a"', b': 1}\n{"b": 2', b'}\n'])
        self.assertEqual(reader.read_line(), b'{"a": 1}')
        self.assertEqual(reader.read_line(), b'{"b": 2}')
        self.assertEqual(stream.read_calls, 3)

    def test_utf8_multibyte_split_across_actual_reads(self):
        # "é" is b"\xc3\xa9"; the two bytes arrive in two SEPARATE read()
        # deliveries and decoding happens only after the complete line.
        reader, stream = self.make_reader(
            chunks=[b'{"k": "\xc3', b'\xa9"}\n'])
        line = reader.read_line()
        self.assertEqual(stream.read_calls, 2)
        self.assertEqual(transport.decode_message(line), {"k": "é"})

    def test_reader_survives_eof_and_keeps_stream_open(self):
        reader, stream = self.make_reader(chunks=[b'{"a": 1}\n'])
        self.assertEqual(reader.read_line(), b'{"a": 1}')
        with self.assertRaises(transport.StreamClosedError):
            reader.read_line()  # scripted EOF
        self.assertFalse(stream.closed,
                         "EOF must not make the reader close the borrowed stream")

    def test_fixture_lifetime_regression_stream_survives_to_teardown(self):
        # Regression for the OSError 9 defect: the reader must retain the
        # stream OBJECT for its whole life. Only the reader holds a live
        # reference here; the fd must not be closed by garbage collection.
        self.pipe = OwnedPipe(self)
        reader = transport.LineReader(self.pipe.reader, timeout=5.0)
        stream = self.pipe.reader
        # Register the stream's close independently BEFORE dropping the
        # OwnedPipe attribute, so teardown stays leak-free while the reader
        # keeps the object alive for the whole test.
        self.addCleanup(stream.close)
        del self.pipe.reader  # drop every external reference to the stream
        gc.collect()
        self.pipe.write(b'{"alive": true}\n')
        line = reader.read_line()
        self.assertEqual(line, b'{"alive": true}')
        self.assertIsNotNone(reader.stream)
        self.assertFalse(reader.stream.closed)


class LineCapTests(unittest.TestCase):
    def make_reader(self, max_line_bytes):
        self.pipe = OwnedPipe(self)
        return transport.LineReader(self.pipe.reader, timeout=5.0,
                                    max_line_bytes=max_line_bytes)

    def test_default_cap_is_32_mib(self):
        self.assertEqual(transport.DEFAULT_MAX_LINE_BYTES, 32 * 1024 * 1024)
        reader = transport.LineReader(ScriptedStream([]))
        self.assertEqual(reader.max_line_bytes, 32 * 1024 * 1024)

    def test_exact_cap_boundary_accepted(self):
        reader = self.make_reader(8)
        self.pipe.write(b'12345678\n')  # exactly 8 payload bytes + newline
        self.assertEqual(reader.read_line(), b'12345678')

    def test_cap_plus_one_refused(self):
        reader = self.make_reader(8)
        self.pipe.write(b'123456789\n')  # 9 payload bytes
        with self.assertRaises(transport.LineTooLongError):
            reader.read_line()

    def test_oversize_line_discarded_before_decoding(self):
        reader = self.make_reader(8)
        self.pipe.write(b'abcdefghij\n')
        with self.assertRaises(transport.LineTooLongError):
            reader.read_line()
        self.assertEqual(reader.pending_bytes, 0)

    def test_multibyte_line_under_cap_accepted(self):
        reader = self.make_reader(8)
        self.pipe.write('éééé\n'.encode("utf-8"))  # 8 payload bytes
        self.assertEqual(reader.read_line(), 'éééé'.encode("utf-8"))


class DecodeMessageTests(unittest.TestCase):
    def test_valid_object(self):
        self.assertEqual(transport.decode_message(b'{"a": 1}'), {"a": 1})

    def test_malformed_json(self):
        with self.assertRaises(transport.MessageError) as caught:
            transport.decode_message(b"this is not json")
        self.assertIn("not valid JSON", str(caught.exception))

    def test_non_object_envelopes_refused(self):
        for raw in (b"[1, 2]", b'"text"', b"null", b"3", b"true"):
            with self.assertRaises(transport.MessageError) as caught:
                transport.decode_message(raw)
            self.assertIn("not a JSON object", str(caught.exception))

    def test_invalid_utf8(self):
        with self.assertRaises(transport.MessageError) as caught:
            transport.decode_message(b'{"a": "\xff\xfe"}')
        self.assertIn("not valid UTF-8", str(caught.exception))

    def test_nonstandard_nan_constant_refused(self):
        with self.assertRaises(transport.MessageError) as caught:
            transport.decode_message('{"a": {"b": NaN}}'.encode("utf-8"))
        self.assertIn("not valid JSON", str(caught.exception))

    def test_nonstandard_infinity_constants_refused(self):
        for raw in ('{"a": [Infinity]}', '{"a": [-Infinity]}',
                    '{"nested": {"deep": [1, Infinity, 2]}}'):
            with self.assertRaises(transport.MessageError) as caught:
                transport.decode_message(raw.encode("utf-8"))
            self.assertIn("nonstandard JSON constant", str(caught.exception))

    def test_non_finite_exponent_refused(self):
        # 1e999 overflows to inf: must be refused, never reserialized as
        # Infinity into an MCP payload.
        for raw in ('{"a": 1e999}', '{"a": -1e999}', '{"x": [0.5e999]}'):
            with self.assertRaises(transport.MessageError) as caught:
                transport.decode_message(raw.encode("utf-8"))
            self.assertIn("non-finite number", str(caught.exception))

    def test_finite_values_and_unicode_round_trip_standard(self):
        line = '{"f": 1.5, "neg": -2.25, "big": 12345678901234567890, "u": "é✓"}'
        value = transport.decode_message(line.encode("utf-8"))
        self.assertEqual(value["u"], "é✓")
        self.assertEqual(value["big"], 12345678901234567890)
        # The decoded value must re-serialize as STANDARD JSON (no NaN/Inf).
        standard = json.dumps(value, ensure_ascii=False, allow_nan=False)
        self.assertEqual(json.loads(standard), value)


class WriteRequestTests(unittest.TestCase):
    def setUp(self):
        self.pipe = None

    def test_small_payload_reaches_pipe(self):
        self.pipe = OwnedPipe(self)
        transport.write_request(self.pipe.writer, b'{"x": 1}\n',
                                time.monotonic() + 5.0)
        self.assertEqual(self.pipe.reader.read(16), b'{"x": 1}\n')

    def test_large_payload_chunked_through_pipe(self):
        import threading
        self.pipe = OwnedPipe(self)
        payload = b'{"blob": "' + b"x" * 150000 + b'"}\n'
        received = bytearray()
        done = threading.Event()

        def drain():
            while len(received) < len(payload):
                try:
                    chunk = self.pipe.reader.read(65536)
                except (OSError, ValueError):
                    break
                if not chunk:
                    break
                received.extend(chunk)
            done.set()

        thread = threading.Thread(target=drain, daemon=True)
        thread.start()
        try:
            transport.write_request(self.pipe.writer, payload,
                                    time.monotonic() + 10.0)
            self.assertTrue(done.wait(timeout=10.0))
        finally:
            thread.join(timeout=5.0)
        self.assertEqual(bytes(received), payload)

    def test_stalled_pipe_hits_write_deadline(self):
        # Nobody reads the pipe: the 64 KiB buffer fills and the write can
        # never complete before the deadline (browser_worker pattern).
        read_fd, write_fd = os.pipe()
        writer = os.fdopen(write_fd, "wb", buffering=0)
        self.addCleanup(writer.close)
        self.addCleanup(os.close, read_fd)
        payload = b"x" * 200000
        started = time.monotonic()
        with self.assertRaises(transport.WriteTimeoutError) as caught:
            transport.write_request(writer, payload, time.monotonic() + 0.4)
        elapsed = time.monotonic() - started
        self.assertLess(elapsed, 5.0)
        message = str(caught.exception)
        self.assertIn("bytes sent", message)
        sent = int(message.split("(")[1].split(" of ")[0])
        self.assertLess(sent, len(payload))

    def test_fd_less_double_gets_whole_payload(self):
        stream = ScriptedStream([])
        transport.write_request(stream, b'{"a": 1}\n', time.monotonic() + 1.0)
        self.assertEqual(stream.writes, [b'{"a": 1}\n'])

    def test_expired_deadline_refuses_immediately(self):
        stream = ScriptedStream([])
        past = time.monotonic() - 1.0
        with self.assertRaises(transport.WriteTimeoutError):
            transport.write_request(stream, b'{"a": 1}\n', past)
        self.assertEqual(stream.writes, [])
        read_fd, write_fd = os.pipe()
        writer = os.fdopen(write_fd, "wb", buffering=0)
        self.addCleanup(writer.close)
        self.addCleanup(os.close, read_fd)
        with self.assertRaises(transport.WriteTimeoutError):
            transport.write_request(writer, b'{"a": 1}\n', past)


class TimeoutConfigTests(unittest.TestCase):
    def test_defaults_are_importable_constants(self):
        self.assertEqual(transport.DEFAULT_STARTUP_TIMEOUT, 60.0)
        self.assertEqual(transport.DEFAULT_REQUEST_TIMEOUT, 90.0)

    def test_completed_pending_line_survives_expired_deadline(self):
        # The deadline bounds WAITING; a line already assembled in the
        # pending buffer is returned without a new wait.
        stream = ScriptedStream([b'{"a": 1}\n{"b": 2}\n'])
        reader = transport.LineReader(stream, timeout=5.0)
        self.assertEqual(reader.read_line(), b'{"a": 1}')
        self.assertEqual(reader.read_line(deadline=time.monotonic() - 1.0),
                         b'{"b": 2}')

    def test_expired_deadline_refuses_reads_of_undelivered_data(self):
        stream = ScriptedStream([b'{"a": 1}\n'])
        reader = transport.LineReader(stream, timeout=5.0)
        with self.assertRaises(transport.ResponseTimeoutError):
            reader.read_line(deadline=time.monotonic() - 1.0)

    def test_invalid_configuration_refused(self):
        with self.assertRaises(ValueError):
            transport.LineReader(ScriptedStream([]), timeout=0)
        with self.assertRaises(ValueError):
            transport.LineReader(ScriptedStream([]), max_line_bytes=0)


if __name__ == "__main__":
    unittest.main()
