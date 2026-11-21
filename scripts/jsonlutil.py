"""JSONL append guard (G24).

Appending to a .jsonl file whose last line has no trailing newline glues
two JSON objects into one invalid line, and the whole file then fails to
parse. Every writer in this repo must go through append_jsonl (or, for the
fd-based writers, ensure_trailing_newline_fd) so a missing terminator is
repaired before the new record lands. verify_jsonl parses a file back and
reports bad line numbers; run it after any push that touches a .jsonl.
"""
import json
from pathlib import Path


def _last_byte_is_newline(path):
    """True when path exists, is non-empty, and ends with b'\\n'."""
    try:
        with open(path, 'rb') as stream:
            stream.seek(-1, 2)
            return stream.read(1) == b'\n'
    except (OSError, ValueError):
        return False


def append_jsonl(path, record):
    """Append one JSON record as its own line, repairing a missing terminator.

    If the file already exists and its last byte is not a newline, a newline
    is written first so the new record starts on its own line. The record is
    dumped with the same compact separators the other writers use.
    """
    path = Path(path)
    line = (json.dumps(record, ensure_ascii=False, separators=(',', ':')) + '\n').encode('utf-8')
    with open(path, 'ab') as stream:
        if path.stat().st_size > 0 and not _last_byte_is_newline(path):
            stream.write(b'\n')
        stream.write(line)


def ensure_trailing_newline_fd(fd, path):
    """For fd-based writers: write b'\\n' first if the file lacks a terminator.

    fd must be open for writing (O_APPEND callers: the byte is appended at
    the end either way). The last byte is read through a separate read-only
    fd because a write-only fd cannot pread. Returns True when a separator
    was written.
    """
    import os
    size = os.fstat(fd).st_size
    if size == 0:
        return False
    read_fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) |
                      getattr(os, 'O_CLOEXEC', 0))
    try:
        if os.pread(read_fd, 1, size - 1) == b'\n':
            return False
    finally:
        os.close(read_fd)
    if os.write(fd, b'\n') != 1:
        raise RuntimeError('jsonl separator write was incomplete')
    return True


def verify_jsonl(path):
    """Parse every line of a .jsonl file; return the bad 1-based line numbers.

    An empty file verifies clean (no lines). A file whose last line lacks a
    trailing newline still verifies clean as long as every line parses.
    """
    bad = []
    with open(path, 'r', encoding='utf-8') as stream:
        for number, line in enumerate(stream, 1):
            if not line.strip():
                bad.append(number)
                continue
            try:
                json.loads(line)
            except ValueError:
                bad.append(number)
    return bad
