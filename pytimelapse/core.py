# coding=utf-8
#
# Copyright 2013 Janne Enberg

import argparse
import imp
import logging
import traceback
import sys
import math
import time
import datetime

import pytimelapse
from filehandler import FileHandler
import media


__doc__ = """Core classes of pytimelapse, main logic"""


class Launcher(object):
    """Handles initialization logic for the application"""

    def start(self):
        """Starts the application"""

        startTime = time.time()

        # Set up logging
        logger = self.get_logger()

        try:
            # Parse arguments
            arguments, parser = self.get_arguments()

            # Load config
            config = self.load_config(arguments, parser)

            logger.debug("Pytimelapse initialized")

            # Start the application
            app = Pytimelapse()
            app.run(config)

            elapsed = str(
                datetime.timedelta(seconds=(time.time() - startTime))
            )

            logger.info(
                "All done, time elapsed: {} ".format(elapsed)
            )

        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()

            if exc_type == SystemExit:
                return

            tracebackItems = traceback.format_exception(
                exc_type,
                exc_value,
                exc_traceback
            )

            message = "Uncaught %(type)s exception: %(value)s " % {
                "type": exc_type,
                "value": exc_value
            }

            message += "\n"

            for item in tracebackItems:
                for line in item.split("\n"):
                    message += '!! ' + line + "\n"

            logger.critical(message)

    def get_arguments(self, arguments=None):
        """Set up an argparser object to parse our command line arguments"""

        description = pytimelapse.__doc__
        parser = argparse.ArgumentParser(description=description)

        parser.add_argument(
            '-c', '--config',
            metavar="filename",
            help="Specify config to be used, defaults to config.py",
            default="config.py"
        )

        parser.add_argument(
            '-s', '--sort',
            metavar="key",
            help="Sort files by absolute path, filename or modified time "
                 "before processing",
            choices=['filepath', 'basename', 'modified']
        )

        parser.add_argument(
            '-v', '--verbose',
            help="Increase output verbosity",
            action="store_true",
            default=None
        )

        parser.add_argument(
            '-q', '--quiet',
            help="Less verbose output",
            action="store_false",
            dest="verbose"
        )

        parser.add_argument(
            '--imageFiles',
            help="Filename patterns to include in timelapse, "
                 "e.g. images/*.jpg",
            nargs="*",
            metavar="pattern"
        )

        parser.add_argument(
            '--codec',
            help="Codec to encode with",
            choices=media.codecs
        )

        parser.add_argument(
            '--outFile',
            help="File to write the video to",
            metavar="filename"
        )

        parser.add_argument(
            '--fps',
            help="Target FPS of the timelapse",
            type=float
        )

        parser.add_argument(
            '--duration',
            help="Target duration of the timelapse, in seconds",
            type=float
        )

        args = parser.parse_args(arguments)

        return args.__dict__, parser

    def load_config(self, arguments, parser):
        """Read our config and merge CLI arguments"""

        config = self.read_config_file(arguments["config"], parser)

        for key in arguments:
            if arguments[key] is None:
                continue

            config[key] = arguments[key]

        return config

    def read_config_file(self, configFile, parser):
        try:
            config_module = imp.load_source('config', configFile)
        except IOError:
            parser.error(
                "Invalid config %(config)s, file not found." % {
                    "config": configFile
                }
            )

        return config_module.config

    def get_logger(self):
        """Initialize the logging system"""

        logger = logging.getLogger("pytimelapse")
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)8s] %(filename)s:%(lineno)i: %'
            '(message)s'
        )

        consoleLogger = logging.StreamHandler()
        consoleLogger.setLevel(logging.DEBUG)
        consoleLogger.setFormatter(formatter)

        logger.addHandler(consoleLogger)

        return logger


class Pytimelapse(object):
    """Handles the timelapse logic"""

    def __init__(self):
        self.logger = logging.getLogger("pytimelapse")
        self.imageHandler = media.ImageHandler()

    def run(self, config):
        self.logger.debug("Scanning for files")

        files = FileHandler().find_files(
            config["imageFiles"],
            config["sortFiles"]
        )

        self.logger.debug("Done, found {} files".format(len(files)))

        fps, duration = self.get_fps_duration(files, config)

        self.logger.info(
            "Resulting file will have {fps:.2f} FPS and last {duration}"
            .format(**{
                "fps": fps,
                "duration": str(datetime.timedelta(seconds=duration))
            })
        )

        files = self.filter_files(files, fps, duration)

        file = files[0]
        frameSize = self.imageHandler.get_frame_size(file)

        self.logger.info(
            "Frames will be {width}x{height}".format(**{
                "width": frameSize[0],
                "height": frameSize[1]
            })
        )

        video = media.VideoHandler(
            config["codec"],
            config["fps"],
            frameSize
        )

        video.open(config["outFile"])

        for i, file in enumerate(files):
            video.write_frame(file)

            if i % math.floor(config["fps"]) == 0:
                duration = i / config["fps"]
                self.logger.info(
                    "Encoded {duration}".format(**{
                        "duration": str(datetime.timedelta(seconds=duration))
                    })
                )

    def filter_files(self, files, fps, duration):
        """Filters given fileset to """

        needFiles = fps * duration
        haveFiles = len(files)

        keepRatio = float(needFiles) / float(haveFiles)

        if keepRatio == 1:
            return files

        newFiles = [files[0]]
        length = 1
        counter = keepRatio

        self.logger.info(
            "Filtering to use {fraction:.2f}% of the {count} available files."
            .format(
                **{
                    "fraction": keepRatio * 100,
                    "count": haveFiles
                }
            )
        )

        for i in range(1, haveFiles):
            counter = counter + keepRatio
            if counter >= length and length < needFiles:
                length = length + 1
                newFiles.append(files[i])

                if length == needFiles:
                    break

        kept = len(newFiles)
        skipped = haveFiles - kept

        self.logger.info(
            "Filtered {skipped} files, {kept} will be used.".format(**{
                "skipped": skipped,
                "kept": kept
            })
        )

        return newFiles

    def get_fps_duration(self, files, config):
        """Calculate FPS and total duration of resulting file"""

        frames = len(files)

        if config["duration"] is None:
            config["duration"] = frames / config["fps"]
        elif config["fps"] is None:
            config["fps"] = frames / config["duration"]

        desiredFrames = config["fps"] * config["duration"]
        if desiredFrames > frames:
            raise ValueError(
                "Frames needed for given FPS ({}) and "
                "duration exceeds available frames ({})"
                .format(
                    desiredFrames, frames
                )
            )

        return config["fps"], config["duration"]
