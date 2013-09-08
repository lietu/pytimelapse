# coding=utf-8
#
# Config for pytimelapse

config = {
    "imageFiles": ['images/*.jpg', 'images/*.png'],
    "verbose": False,
    # Configure either FPS or duration, not both
    "fps": 60,
    "duration": None,
    "sortFiles": "filename"
}
