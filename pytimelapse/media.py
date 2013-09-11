# coding=utf-8
#
# Copyright 2013 Janne Enberg
import cv2


# List of supported codec names for OpenCV
codecs = {
    "PIM1": "MPEG-1",
    "MJPG": "motion-jpeg",
    "MP42": "MPEG-4.2",
    "DIV3": "MPEG-4.3",
    "DIVX": "MPEG-4",
    "U263": "H263",
    "I263": "H263I",
    "FLV1": "FLV1"
}


class VideoHandler(object):
    """Some abstraction for OpenCV VideoWriter"""

    def __init__(self, codec, fps, frameSize):
        self.fourcc = self.codec2fourcc(codec)
        self.fps = fps
        self.frameSize = frameSize

    def open(self, filename):
        """Open a video writer"""
        self.videoWriter = cv2.VideoWriter(
            filename,
            self.fourcc,
            self.fps,
            self.frameSize
        )

    def write_frame(self, filename):
        """Write the given file as a frame in the video"""

        self.videoWriter.write(cv2.imread(filename))

    def codec2fourcc(self, codec):
        """Convert codecs dict keys to OpenCV FOURCC codes"""

        # Convert "DIVX" -> ['D', 'I', 'V', 'X']
        args = list(codec)

        return cv2.cv.CV_FOURCC(*args)


class ImageHandler(object):
    """Some abstraction for OpenCV images"""

    def open(self, filename):
        """Open an image with OpenCV"""
        return cv2.cv.LoadImage(filename)

    def get_size(self, filename):
        """Get the width and height of the image file"""

        image = self.open(filename)

        return (image.width, image.height)
