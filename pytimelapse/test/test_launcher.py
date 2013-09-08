# coding=utf-8
#
# Copyright 2013 Janne Enberg

from mock import Mock
from unittest import TestCase
from pytimelapse.core import Launcher


class TestLauncher(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_config_1(self):
        fakeArguments = [
            '--config=fake_config.py',
            '--imageFiles', 'images/*.png', 'images/*.gif',
            '--fps=60',
            '--verbose'
        ]

        fakeConfig = {
            "imageFiles": ['images/*.jpg'],
            "verbose": False,
            "fps": None,
            "duration": None
        }

        expected = {
            "config": "fake_config.py",
            "verbose": True,
            "fps": 60,
            "duration": None,
            "imageFiles": ['images/*.png', 'images/*.gif']
        }

        launcher = Launcher()
        launcher.read_config_file = Mock(return_value=fakeConfig)
        launcher.check_args = Mock(return_value=True)

        arguments, parser = launcher.get_arguments(fakeArguments)
        config = launcher.load_config(arguments, parser)

        self.assertEqual(expected, config)

    def test_get_config_2(self):
        fakeArguments = [
            '--fps=30',
            '--quiet'
        ]

        fakeConfig = {
            "imageFiles": ['images/*.jpg', 'images/*.png', 'images/*.gif'],
            "verbose": True,
            "fps": None,
            "duration": 60.0
        }

        expected = {
            "config": "config.py",
            "verbose": False,
            "fps": 30.0,
            "duration": 60.0,
            "imageFiles": ['images/*.jpg', 'images/*.png', 'images/*.gif']
        }

        launcher = Launcher()
        launcher.read_config_file = Mock(return_value=fakeConfig)
        launcher.check_args = Mock(return_value=True)

        arguments, parser = launcher.get_arguments(fakeArguments)
        config = launcher.load_config(arguments, parser)

        self.assertEqual(expected, config)
