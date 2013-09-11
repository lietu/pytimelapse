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

    def __init__(self):
        self.logger = None

    def start(self):
        """Starts the application"""

        startTime = time.time()

        try:
            config = ConfigHandler().get_config()

            # Set up logging
            logger = self.get_logger(config)

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
            # Get exception data
            exc_type, exc_value, exc_traceback = sys.exc_info()

            # If sys.exit(), ignore
            if exc_type == SystemExit:
                return

            # Collect traceback
            tracebackItems = traceback.format_exception(
                exc_type,
                exc_value,
                exc_traceback
            )

            # Make a pretty error message
            message = "Uncaught {type} exception: {value} ".format(**{
                "type": exc_type,
                "value": exc_value
            })
            message += "\n"

            # Prepend all lines with !! to make it very clear that this is
            # an error
            for item in tracebackItems:
                for line in item.split("\n"):
                    message += '!! ' + line + "\n"

            # Throw it to the logger
            logger = self.get_logger()
            logger.critical(message)

    def get_logger(self, config=None):
        """Initialize the logging system"""

        # If already initialized, do nothing
        if self.logger:
            return self.logger

        # Get a logger
        logger = logging.getLogger("pytimelapse")

        # Make the logger itself catch all messages
        logger.setLevel(logging.DEBUG)

        # Format it to include even more data
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)8s] %(filename)s:%(lineno)i: %'
            '(message)s'
        )

        # Create a handler to log into the console
        consoleLogger = logging.StreamHandler()

        # Pick a verbosity level for the console
        if config is None or config["verbosity"] >= 2:
            consoleLogger.setLevel(logging.DEBUG)
        elif config["verbosity"] >= 1:
            consoleLogger.setLevel(logging.INFO)
        else:
            consoleLogger.setLevel(logging.ERROR)

        # Make sure we format console output
        consoleLogger.setFormatter(formatter)

        # Make the logger route the logs to the console handler
        logger.addHandler(consoleLogger)

        self.logger = logger

        return logger


class Pytimelapse(object):
    """Handles the timelapse logic"""

    def __init__(self):
        self.logger = logging.getLogger("pytimelapse")

    def run(self, config):
        """Main application logic"""

        self.logger.debug("Scanning for files")

        fileHandler = FileHandler()

        # Find the image frames
        files = fileHandler.find_files(config)

        if len(files) == 0:
            raise Exception("No image files found")

        self.logger.debug("Done, found {} files".format(len(files)))

        files = fileHandler.filter_files(files, config)

        self.logger.debug("Filtered to {} files".format(len(files)))

        # And now we have to recalculate final FPS and duration
        fps, duration = self.get_fps_duration(files, config)

        self.logger.info(
            "Resulting file will have {fps:.2f} FPS and last {duration}"
            .format(**{
                "fps": fps,
                "duration": str(datetime.timedelta(seconds=duration))
            })
        )

        # Figure out the frame size for the video, picking the size of the
        # first image
        frameSize = media.ImageHandler().get_size(files[0])

        self.logger.info(
            "Frames will be {width}x{height}".format(**{
                "width": frameSize[0],
                "height": frameSize[1]
            })
        )

        # Start video handler
        video = media.VideoHandler(
            config["codec"],
            config["fps"],
            frameSize
        )

        video.open(config["outFile"])

        # Go through frames
        for i, file in enumerate(files):
            # Write
            video.write_frame(file)

            # Update user occasionally about our progress
            if i % math.floor(config["fps"]) == 0:
                duration = i / config["fps"]
                self.logger.info(
                    "Encoded {duration}".format(**{
                        "duration": str(datetime.timedelta(seconds=duration))
                    })
                )

    def get_fps_duration(self, files, config):
        """Calculate FPS and total duration of resulting file"""

        frames = len(files)

        fps = config["fps"]
        duration = config["duration"]

        if duration is None:
            duration = frames / fps
        elif fps is None:
            fps = frames / duration

        return fps, duration


class ConfigHandler(object):
    """Handle's software configuration"""

    def get_config(self):
        """Parse CLI args and config file and merge them"""

        # Parse arguments
        arguments, parser = self.get_arguments()

        # Load config
        config = self.load_config(arguments, parser)

        # Check that we have necessary data
        self.check_config(config, parser)

        return config

    def get_arguments(self, arguments=None):
        """Parse our command-line arguments"""

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
            metavar="KEY",
            help="Sort files by absolute \"filepath\", "
                 "\"basename\" or \"modified\" time "
                 "before processing",
            choices=['filepath', 'basename', 'modified']
        )

        parser.add_argument(
            '-v', '--verbose',
            help="Increase output verbosity",
            action="count"
        )

        parser.add_argument(
            '-q', '--quiet',
            help="Less verbose output",
            action="count"
        )

        parser.add_argument(
            '--imageFiles',
            help="Filename patterns to include in timelapse, "
                 "e.g. images/*.jpg",
            nargs="*",
            metavar="PATTERN"
        )

        parser.add_argument(
            '--codec',
            help="Codec to encode with",
            choices=media.codecs
        )

        parser.add_argument(
            '--outFile',
            help="File to write the video to",
            metavar="FILENAME"
        )

        parser.add_argument(
            '--fps',
            help="Target FPS of the timelapse",
            type=float
        )

        parser.add_argument(
            '--duration',
            help="Target duration of the timelapse, in seconds",
            type=float,
            metavar="SECONDS"
        )

        parser.add_argument(
            '--startFile',
            help="Skip all the files sorted before the given file",
            metavar="FILENAME"
        )

        parser.add_argument(
            '--useNthFile',
            help="Only use every Nth file, good in combination with "
                 "startFile",
            type=int,
            metavar="N"
        )

        parser.add_argument(
            '--onlyBetweenTimes',
            help="Only include images taken between the timestamps, Will pick "
                 "last number in filename and assume it's a unix timestamp, "
                 "then filter based on the given time range",
            metavar="HH:MM:SS-HH:MM:SS"
        )

        parser.add_argument(
            '--timestampTimezone',
            help="Parse the file timestamp as if from the given timezone",
            metavar="TIMEZONE"
        )

        args = parser.parse_args(arguments)

        return args.__dict__, parser

    def load_config(self, arguments, parser):
        """Read our config and merge CLI arguments"""

        config = self.read_config_file(arguments["config"], parser)

        for key in arguments:
            if arguments[key] is None:
                continue

            if key == "verbose":
                config["verbosity"] += arguments[key]
            elif key == "quiet":
                config["verbosity"] -= arguments[key]
            else:
                config[key] = arguments[key]

        return config

    def read_config_file(self, configFile, parser):
        """Read the actual config file"""

        try:
            config_module = imp.load_source('config', configFile)
        except IOError:
            parser.error(
                "Invalid config {}, file not found.".format(configFile)
            )

        return config_module.config

    def check_config(self, config, parser):
        """Check the config for sanity"""

        if config["fps"] is None and config["duration"] is None:
            parser.error("Invalid config, no FPS or duration specified .")
