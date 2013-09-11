# coding=utf-8
#
# Copyright 2013 Janne Enberg

import os
from mock import Mock
from unittest import TestCase
from logging import Logger

from pytimelapse.filehandler import FileHandler
from pytimelapse.filehandler import File


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
            os.path.join(absPath, "1.txt"),
            os.path.join(absPath, "2.txt"),
            os.path.join(absPath, "3.txt")
        ]

        patterns = [
            os.path.join(absPath, "*.txt"),
            os.path.join(absPath, "*.jpg")
        ]

        config = {
            "imageFiles": patterns,
            "sortFiles": "filepath",
            "startFile": None,
            "onlyBetweenTimes": None
        }

        files = fileHandler.find_files(config)
        self.assertEqual(expected, files)

        patterns = [
            os.path.join(absPath, "1.txt"),
            os.path.join(absPath, "2.txt"),
            os.path.join(absPath, "3.txt")
        ]

        config = {
            "imageFiles": patterns,
            "sortFiles": "filepath",
            "startFile": None,
            "onlyBetweenTimes": None
        }

        files = fileHandler.find_files(config)
        self.assertEqual(expected, files)

        del expected[2]

        patterns = [
            os.path.join(absPath, "[12].txt")
        ]

        config = {
            "imageFiles": patterns,
            "sortFiles": "filepath",
            "startFile": None,
            "onlyBetweenTimes": None
        }

        files = fileHandler.find_files(config)
        self.assertEqual(expected, files)

    def test_sort_files(self):
        fileHandler = FileHandler()

        absPath = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "files"
        )

        filenames = [
            os.path.join(absPath, "1.txt"),
            os.path.join(absPath, "2.txt"),
            os.path.join(absPath, "3.txt")
        ]

        self.touch(filenames[2], 1)
        self.touch(filenames[1], 2)
        self.touch(filenames[0], 3)

        files = [
            File(filenames[0]),
            File(filenames[1]),
            File(filenames[2])
        ]

        unsorted = [
            files[1],
            files[2],
            files[0],
        ]

        sortedFiles = fileHandler.sort_objects(unsorted, sortKey="filepath")
        self.assertEqual(files, sortedFiles)

        files.reverse()
        sortedFiles = fileHandler.sort_objects(unsorted, sortKey="modified")
        self.assertEqual(files, sortedFiles)

    def test_start_from(self):
        fileHandler = FileHandler()

        absPath = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "files"
        )

        files = [
            File(os.path.join(absPath, "1.txt")),
            File(os.path.join(absPath, "2.txt")),
            File(os.path.join(absPath, "3.txt"))
        ]

        filtered = fileHandler.start_from(files, files[1].filepath)
        del files[0]

        self.assertEqual(files, filtered)

    def test_filter_times(self):
        fileHandler = FileHandler()

        absPath = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "files"
        )

        filenames = [
            os.path.join(absPath, "1.txt"),
            os.path.join(absPath, "2.txt"),
            os.path.join(absPath, "3.txt")
        ]

        self.touch(filenames[2], 1)
        self.touch(filenames[1], 2)
        self.touch(filenames[0], 3)

        files = [
            File(filenames[0]),
            File(filenames[1]),
            File(filenames[2])
        ]

        config = {
            "onlyBetweenTimes": "00:00:02-00:00:02",
            "timestampTimezone": "UTC"
        }

        expected = [
            files[1]
        ]

        filtered = fileHandler.filter_times(files, config)
        self.assertEqual(expected, filtered)

    def test_filter_files(self):
        fileHandler = FileHandler()
        fileHandler.logger = Mock(Logger)

        absPath = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "files"
        )

        files = [
            File(os.path.join(absPath, "1.txt")),
            File(os.path.join(absPath, "2.txt")),
            File(os.path.join(absPath, "3.txt"))
        ]

        config = {
            "useNthFile": None,
            "fps": 2,
            "duration": 1
        }

        expected = [
            files[0],
            files[1]
        ]

        filtered = fileHandler.filter_files(files, config)
        self.assertEqual(expected, filtered)

    def touch(self, filename, timestamp=None):
        with file(filename, 'a'):
            os.utime(filename, (timestamp, timestamp))
