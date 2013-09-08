# coding=utf-8
#
# Copyright 2013 Janne Enberg

import argparse
import imp
import logging
import traceback
import sys

import pytimelapse
from filehandler import FileHandler


__doc__ = """Core classes of pytimelapse, main logic"""


class Launcher(object):
    """Handles initialization logic for the application"""

    def start(self):
        """Starts the application"""

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
            help="Sort files by filename or modified time before processing",
            choices=['filename', 'modified']
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

        # FPS or duration group
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            '--fps',
            help="Target FPS of the timelapse",
            type=float
        )

        group.add_argument(
            '--duration',
            help="Target duration of the timelapse, in seconds",
            type=float
        )
        # End group

        args = parser.parse_args(arguments)

        return args.__dict__, parser

    def load_config(self, arguments, parser):
        """Read our config and merge CLI arguments"""

        config = self.read_config_file(arguments["config"], parser)

        for key in arguments:
            if arguments[key] is None:
                continue

            if key == "fps":
                config["duration"] = None
            elif key == "duration":
                config["fps"] = None

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

    def run(self, config):
        files = FileHandler().find_files(
            config["imageFiles"],
            config["sortFiles"]
        )

        fps, duration = self.get_fps_duration(files, config)

        self.logger.info(
            "Resulting file will have {fps:.2f} FPS and last {duration:.2f} "
            "seconds".format(**{
                "fps": fps,
                "duration": duration
            })
        )

    def get_fps_duration(self, files, config):
        """Calculate FPS and total duration of resulting file"""

        frames = len(files)


        if config["fps"]:
            fps = config["fps"]
            duration = frames / fps
        else:
            duration = config["duration"]
            fps = frames / duration

        return fps, duration
