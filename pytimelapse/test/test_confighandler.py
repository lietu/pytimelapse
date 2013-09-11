# coding=utf-8
#
# Copyright 2013 Janne Enberg

from mock import Mock
from unittest import TestCase
from pytimelapse.core import ConfigHandler


class TestConfigHandler(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_config_1(self):
        fakeArguments = [
            '--config=fake_config.py',
            '--imageFiles', 'images/*.png', 'images/*.gif',
            '--fps=60',
            '-vv'
        ]

        fakeConfig = {
            "imageFiles": ['images/*.jpg'],
            "verbosity": 0,
            "fps": None,
            "duration": None
        }

        expected = {
            "config": "fake_config.py",
            "verbosity": 2,
            "fps": 60,
            "duration": None,
            "imageFiles": ['images/*.png', 'images/*.gif']
        }

        handler = ConfigHandler()
        handler.read_config_file = Mock(return_value=fakeConfig)
        handler.check_args = Mock(return_value=True)

        arguments, parser = handler.get_arguments(fakeArguments)
        config = handler.load_config(arguments, parser)

        self.assertEqual(expected, config)

    def test_get_config_2(self):
        fakeArguments = [
            '--fps=30',
            '--quiet'
        ]

        fakeConfig = {
            "imageFiles": ['images/*.jpg', 'images/*.png', 'images/*.gif'],
            "verbosity": 1,
            "fps": None,
            "duration": 60.0
        }

        expected = {
            "config": "config.py",
            "verbosity": 0,
            "fps": 30.0,
            "duration": 60.0,
            "imageFiles": ['images/*.jpg', 'images/*.png', 'images/*.gif']
        }

        handler = ConfigHandler()
        handler.read_config_file = Mock(return_value=fakeConfig)
        handler.check_args = Mock(return_value=True)

        arguments, parser = handler.get_arguments(fakeArguments)
        config = handler.load_config(arguments, parser)

        self.assertEqual(expected, config)
