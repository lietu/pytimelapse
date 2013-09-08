# coding=utf-8
#
# Copyright 2013 Janne Enberg
import cv2


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
    def __init__(self, codec, fps, frameSize):
        self.fourcc = self.codec2fourcc(codec)
        self.fps = fps
        self.frameSize = frameSize

    def open(self, filename):
        self.videoWriter = cv2.VideoWriter(
            filename,
            self.fourcc,
            self.fps,
            self.frameSize,
            1
        )

    def write_frame(self, filename):
        self.videoWriter.write(cv2.imread(filename))

    def codec2fourcc(self, codec):
        # Convert "DIVX" -> ['D', 'I', 'V', 'X']
        args = list(codec)

        return cv2.cv.CV_FOURCC(*args)


class ImageHandler(object):
    def open(self, filename):
        return cv2.cv.LoadImage(filename)

    def get_frame_size(self, filename):
        image = self.open(filename)

        return (image.width, image.height)
