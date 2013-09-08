# coding=utf-8
#
# Copyright 2013 Janne Enberg

import os
from unittest import TestCase
from pytimelapse.filehandler import FileHandler


class TestFileHandler(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_find_files(self):
        fileHandler = FileHandler()

        absPath = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "files"
        )

        expected = [
            os.path.join(absPath, "1"),
            os.path.join(absPath, "2"),
            os.path.join(absPath, "3")
        ]

        patterns = [
            os.path.join(absPath, "*"),
            os.path.join(absPath, "*.jpg")
        ]

        files = fileHandler.find_files(patterns, "filepath")
        self.assertEqual(expected, files)

        patterns = [
            os.path.join(absPath, "1"),
            os.path.join(absPath, "2"),
            os.path.join(absPath, "3")
        ]

        files = fileHandler.find_files(patterns, "basename")
        self.assertEqual(expected, files)

        del expected[2]

        patterns = [
            os.path.join(absPath, "[12]")
        ]

        files = fileHandler.find_files(patterns, "basename")
        self.assertEqual(expected, files)

    def test_sort_files(self):
        fileHandler = FileHandler()

        absPath = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "files"
        )

        files = [
            os.path.join(absPath, "1"),
            os.path.join(absPath, "2"),
            os.path.join(absPath, "3")
        ]

        self.touch(files[2], 1)
        self.touch(files[1], 2)
        self.touch(files[0], 3)

        unsorted = [
            files[1],
            files[2],
            files[0]
        ]

        sortedFiles = fileHandler.sort_files(unsorted, sortKey="filepath")
        self.assertEqual(files, sortedFiles)

        files.reverse()
        sortedFiles = fileHandler.sort_files(unsorted, sortKey="modified")
        self.assertEqual(files, sortedFiles)

    def touch(self, filename, timestamp=None):
        with file(filename, 'a'):
            os.utime(filename, (timestamp, timestamp))
