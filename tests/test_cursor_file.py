"""Native cursor-file validator: compile a standalone harness against the real header.

No plugin build or load, no renderer. The harness includes
native/cursor-file.hpp directly and reports ok/error per fixture file.
"""
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / 'native/cursor-file.hpp'

HARNESS = r'''
#include <iostream>
#include "cursor-file.hpp"
int main(int argc, char** argv) {
    if (argc != 2) return 2;
    try {
        auto bytes = cursorFile(argv[1]);
        std::cout << "ok " << bytes.size() << "\n";
        return 0;
    } catch (const std::exception& e) {
        std::cout << "error " << e.what() << "\n";
        return 1;
    }
}
'''


def xcursor(size=32, width=None, height=None, file_version=0x10000,
            image_version=1, count=1, magic=0x72756358):
    """One nominal image at the table offset; mirrors the python fixture layout."""
    width = size if width is None else width
    height = size if height is None else height
    hot = min(max(1, size // 16), max(width, height) - 1) if min(width, height) > 1 else 0
    pixels = struct.pack('<I', 0xFF000000) * (width * height)
    chunk = struct.pack('<IIIIIIIII', 36, 0xFFFD0002, size, image_version,
                        width, height, hot, hot, 0) + pixels
    table = b''.join(struct.pack('<III', 0xFFFD0002, size, 16 + 12 * count)
                     for _ in range(count))
    return struct.pack('<IIII', magic, 16, file_version, count) + table + chunk


@unittest.skipUnless(shutil.which('g++'), 'g++ unavailable')
class CursorFileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.tmp.cleanup)
        folder = Path(cls.tmp.name)
        (folder / 'harness.cpp').write_text(HARNESS)
        cls.binary = folder / 'cursor-file-harness'
        try:
            subprocess.run(['g++', '-std=c++26', '-O1', '-I', str(HEADER.parent),
                            str(folder / 'harness.cpp'), '-o', str(cls.binary)],
                           capture_output=True, text=True, check=True, timeout=300)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            raise RuntimeError('harness compile failed: %s' %
                               getattr(exc, 'stderr', exc)) from exc

    def check(self, data, expect_ok=True):
        target = Path(self.tmp.name) / 'fixture'
        target.write_bytes(data)
        done = subprocess.run([str(self.binary), str(target)],
                              capture_output=True, text=True, timeout=30)
        if expect_ok:
            self.assertEqual(done.returncode, 0, done.stdout)
            self.assertTrue(done.stdout.startswith('ok '))
            self.assertEqual(int(done.stdout.split()[1]), len(data))
        else:
            self.assertNotEqual(done.returncode, 0, done.stdout)
            self.assertTrue(done.stdout.startswith('error '))
        return done.stdout

    def test_valid_fixture_reports_immutable_bytes(self):
        self.check(xcursor())

    def test_symlink_to_regular_file_reads_through(self):
        target = Path(self.tmp.name) / 'real'
        target.write_bytes(xcursor())
        link = Path(self.tmp.name) / 'alias'
        link.symlink_to(target)
        done = subprocess.run([str(self.binary), str(link)],
                              capture_output=True, text=True, timeout=30)
        self.assertEqual(done.returncode, 0, done.stdout)

    def test_malformed_magic_and_versions_refused(self):
        self.check(xcursor(magic=0x0), expect_ok=False)
        self.check(xcursor(file_version=0x20000), expect_ok=False)
        self.check(xcursor(image_version=2), expect_ok=False)

    def test_truncated_and_short_files_refused(self):
        full = xcursor()
        for cut in (15, 16, len(full) // 2, len(full) - 1):
            with self.subTest(cut=cut):
                self.check(full[:cut], expect_ok=False)
        self.check(b'', expect_ok=False)

    def test_table_offset_past_end_refused(self):
        header = struct.pack('<IIII', 0x72756358, 16, 0x10000, 1)
        table = struct.pack('<III', 0xFFFD0002, 32, 10**6)
        self.check(header + table, expect_ok=False)

    def test_oversized_dimensions_and_hotspots_refused(self):
        self.check(xcursor(size=32, width=2048), expect_ok=False)
        self.check(xcursor(size=32, height=2049), expect_ok=False)
        blob = bytearray(xcursor())
        # xhot at chunk offset+24: force it past the width.
        struct.pack_into('<I', blob, 28 + 24, 10**6)
        self.check(bytes(blob), expect_ok=False)

    def test_empty_table_and_missing_image_refused(self):
        header = struct.pack('<IIII', 0x72756358, 16, 0x10000, 0)
        self.check(header, expect_ok=False)
        header = struct.pack('<IIII', 0x72756358, 16, 0x10000, 1)
        table = struct.pack('<III', 0x00000001, 32, 28)
        self.check(header + table + b'\0' * 64, expect_ok=False)

    def test_fifo_and_oversize_sparse_refused(self):
        import os
        fifo = Path(self.tmp.name) / 'pipe'
        os.mkfifo(fifo)
        done = subprocess.run([str(self.binary), str(fifo)],
                              capture_output=True, text=True, timeout=30)
        self.assertNotEqual(done.returncode, 0, done.stdout)
        big = Path(self.tmp.name) / 'big'
        with open(big, 'wb') as stream:
            stream.truncate(17 * 1024 * 1024)
        done = subprocess.run([str(self.binary), str(big)],
                              capture_output=True, text=True, timeout=30)
        self.assertNotEqual(done.returncode, 0, done.stdout)


if __name__ == '__main__':
    unittest.main()
