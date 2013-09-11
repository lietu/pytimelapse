# coding=utf-8
#
# Config for pytimelapse

config = {
    # List of Unix shell compatible patterns for searching images
    "imageFiles": ['images/*.jpg', 'images/*.png'],

    # What file to write to
    "outFile": "timelapse.avi",

    # 1 = Some output, 2 = Lots of output, 0 = Only errors
    "verbosity": 1,

    # How to sort the image files:
    # - basename: the filename regardless of path
    # - modified: modified time
    # - filepath: full path to file incl. filename
    "sortFiles": "filepath",

    # Which codec to use, supported options:
    # PIM1: MPEG-1,
    # MJPG: motion-jpeg,
    # MP42: MPEG-4.2,
    # DIV3: MPEG-4.3,
    # DIVX: MPEG-4,
    # U263: H263,
    # I263: H263I,
    # FLV1: FLV1
    "codec": "DIVX",

    # Frames per second to record at
    "fps": 60,

    # Duration to aim for, can be used instead of FPS, or in combination with
    # FPS. If both FPS and duration is given, it will skip files to achieve
    # desired length with the given FPS
    "duration": None,

    # Skip files until this file is encountered in the sorted results
    "startFile": None,

    # Filter to use only every Nth file, e.g. if known to have 1 image per
    # minute, a value of 1440 should give you a picture at the same time on
    # every day
    "useNthFile": None,

    # Only include images taken between the timestamps XX:XX:XX-YY:YY:YY
    # Will pick last number in filename and assume it's a unix timestamp,
    # then filter based on the given time range
    "onlyBetweenTimes": None,

    # Parse the file timestamp as if from the given timezone, None for local
    "timestampTimezone": "GMT"
}
