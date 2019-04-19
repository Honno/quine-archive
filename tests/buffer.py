import unittest
import io

import bitstring

import quine_archive

class TestQuineBuffer(unittest.TestCase):
    buf = None

    def setUp(self):
        self.buf = quine_archive.QuineBuffer()

    def tearDown(self):
        self.buf = None

    def test_literal(self):
        self.buf.lit(0)
        self.assertEqual(self.buf.bytes_array(), b'\x00\x00\x00\xff\xff')
