# coding=utf-8
#
# Copyright 2013 Janne Enberg
import glob
import os


__doc__ = """File utilities for Pytimelapse"""


class FileHandler(object):
    def find_files(self, patterns, sortKey):
        """Find the files by the list of glob patterns, sort them by sortKey"""

        files = []
        for pattern in patterns:
            files = files + glob.glob(pattern)

        files = self.sort_files(files, sortKey)

        return files

    def sort_files(self, files, sortKey):
        """Sort the given filelist based on an attribute,
        e.g. filename or modified time

        Valid sortKey values are: filename, modified"""

        fileData = [File(file) for file in files]

        # Sort by whatever property is desired
        fileData.sort(key=lambda file: file.__dict__[sortKey])

        # Extract filenames back from that
        newFiles = [file.filepath for file in fileData]

        return newFiles


class File(object):
    def __init__(self, filename):
        self.filepath = os.path.abspath(filename)
        self.basename = os.path.basename(filename)
        self.modified = os.path.getmtime(filename)
