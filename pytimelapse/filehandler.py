# coding=utf-8
#
# Copyright 2013 Janne Enberg
import glob
import os
import re
from datetime import datetime
from pytz import timezone


__doc__ = """File utilities for Pytimelapse"""


class FileHandler(object):
    def find_files(self, config):
        """Find the files by the list of glob patterns, sort them by sortKey"""

        files = []
        for pattern in config["imageFiles"]:
            files = files + glob.glob(pattern)

        # Convert to File objects
        fileData = [File(file) for file in files]

        fileData = self.sort_objects(fileData, config["sortFiles"])

        if config["startFile"]:
            fileData = self.start_from(fileData, config["startFile"])
        if config["onlyBetweenTimes"]:
            fileData = self.filter_times(fileData, config)

        # Convert back to a list of absolute paths
        files = [file.filepath for file in fileData]

        return files

    def sort_objects(self, objectList, sortKey):
        """Sort the given list of objects based on a property"""

        # Sort by whatever property is desired
        objectList.sort(key=lambda object: object.__dict__[sortKey])

        return objectList

    def start_from(self, files, search):
        """Filter file list to start from the file we wanted to skip to"""

        search = os.path.abspath(search)

        found = False
        temp = []

        for file in files:
            if file.filepath == search:
                found = True
            if found:
                temp.append(file)

        return temp

    def filter_times(self, files, config):
        """Filter by time range"""

        min, max = config["onlyBetweenTimes"].split("-")
        min = min.strip()
        max = max.strip()

        # Parse given times into datetime.time objects
        minTime = datetime.strptime(min, "%H:%M:%S").time()
        maxTime = datetime.strptime(max, "%H:%M:%S").time()

        matches = []

        tz = None
        if config["timestampTimezone"]:
            tz = timezone(config["timestampTimezone"])

        for file in files:

            # Find the last number in the filename
            filename = re.findall(r'\d+', file.filepath)[-1]

            # Assume that's a unix timestamp, convert to datetime.time
            fileTime = datetime.fromtimestamp(int(filename), tz).time()

            # Check if it's between min and max
            if fileTime >= minTime and fileTime <= maxTime:
                matches.append(file)

        return matches

    def filter_files(self, files, config):
        """Filters given fileset to a maximum FPS and duration"""

        if config["useNthFile"]:
            newFiles = files[::config["useNthFile"]]
        else:
            haveFiles = len(files)

            # If we only have an FPS or duration, we don't want to filter here
            if config["fps"] is None or config["duration"] is None:
                return files

            # Calculate how many files we need for the FPS and duration given
            needFiles = config["fps"] * config["duration"]

            if needFiles > haveFiles:
                raise ValueError(
                    "Frames needed for given FPS ({}) and "
                    "duration exceeds available frames ({})"
                    .format(
                        needFiles, haveFiles
                    )
                )

            # Calculate ratio of how many files we need to keep
            keepRatio = float(needFiles) / float(haveFiles)

            # 100% = return all
            if keepRatio == 1:
                return files

            self.logger.info(
                "Filtering to use {fraction:.2f}% of the {count} available "
                "files."
                .format(
                    **{
                        "fraction": keepRatio * 100,
                        "count": haveFiles
                    }
                )
            )

            # Start collecting a filtered file list from the first file
            newFiles = [files[0]]
            length = 1
            counter = keepRatio

            # Loop through the files
            for i in range(1, haveFiles):

                # Increment a counter based on the ratio
                counter = counter + keepRatio

                # If we need a new file
                if counter >= length and length < needFiles:

                    # Throw in one more file
                    newFiles.append(files[i])
                    length = length + 1

                    # Break out when we have enough
                    if length == needFiles:
                        break

            # Check result
            kept = len(newFiles)
            skipped = haveFiles - kept

            self.logger.info(
                "Filtered {skipped} files, {kept} will be used.".format(**{
                    "skipped": skipped,
                    "kept": kept
                })
            )

        return newFiles


class File(object):
    def __init__(self, filename):
        self.filepath = os.path.abspath(filename)
        self.basename = os.path.basename(filename)
        self.modified = os.path.getmtime(filename)
