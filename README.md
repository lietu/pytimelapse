# Pytimelapse

## Description

Tool to generate timelapse videos from a collection of snapshot images.

I made this tool, because I had about 200,000 images collected over a few months at regular intervals and I wanted to turn that into a timelapse. None of the existing tools seemed to be able to even handle that amount of image files, much less produce anything sane out of a large amount of files.

E.g. with 30 FPS speed, 200,000 images would've taken almost 2 hours to view, and it's not like I could bump up the FPS to 600+ to keep the video down to 5 minutes in length.

So I made my own tool, which could handle a fairly large set of images, and filter the list if necessary to achieve desired FPS and duration limits. I pointed it at my images and some 15 minutes later I had a timelapse file.


## Installation

Just clone the code locally and install the dependency, which is OpenCV (and numpy + ffmpeg for it).

Configuring OpenCV (and ffmpeg) was at least for me very painful. If you end up with pytimelapse generating empty files, check out [a StackOverflow solution](http://stackoverflow.com/questions/11699298/opencv-2-4-videocapture-not-working-on-windows).

Basically what I had to do was rougly along the lines of:
 * Download OpenCV to C:\opencv
 * Add c:\opencv\3rdparty\ffmpeg to my PATH
 * Copy opencv_ffmpeg.dll to opencv_ffmpeg246.dll
 * Create "C:\Python27\Lib\site-packages\cv2.pth" with the contents "C:\opencv\build\python\2.7\"
 * Possibly something more I can't remember

There are limited tests, which you can run e.g. by installing nose and mock, and then running

```
nosetests
```


## Usage

You can configure the parameters via config.py, or override them all on the commandline. Most things should be fairly self-explanatory, just run:

```
python pytimelapse.py --help
```

```
usage: pytimelapse.py [-h] [-c filename] [-s KEY] [-v] [-q]
                      [--imageFiles [PATTERN [PATTERN ...]]]
                      [--codec {I263,FLV1,U263,MP42,MJPG,PIM1,DIVX,DIV3}]
                      [--outFile FILENAME] [--fps FPS] [--duration SECONDS]
                      [--startFile FILENAME] [--useNthFile N]
                      [--onlyBetweenTimes HH:MM:SS-HH:MM:SS]
                      [--timestampTimezone TIMEZONE]

Generates timelapse videos from a collection of snapshot images.

optional arguments:
  -h, --help            show this help message and exit
  -c filename, --config filename
                        Specify config to be used, defaults to config.py
  -s KEY, --sort KEY    Sort files by absolute "filepath", "basename" or
                        "modified" time before processing
  -v, --verbose         Increase output verbosity
  -q, --quiet           Less verbose output
  --imageFiles [PATTERN [PATTERN ...]]
                        Filename patterns to include in timelapse, e.g.
                        images/*.jpg
  --codec {I263,FLV1,U263,MP42,MJPG,PIM1,DIVX,DIV3}
                        Codec to encode with
  --outFile FILENAME    File to write the video to
  --fps FPS             Target FPS of the timelapse
  --duration SECONDS    Target duration of the timelapse, in seconds
  --startFile FILENAME  Skip all the files sorted before the given file
  --useNthFile N        Only use every Nth file, good in combination with
                        startFile
  --onlyBetweenTimes HH:MM:SS-HH:MM:SS
                        Only include images taken between the timestamps, Will
                        pick last number in filename and assume it's a unix
                        timestamp, then filter based on the given time range
  --timestampTimezone TIMEZONE
                        Parse the file timestamp as if from the given timezone

```


## License

new BSD or MIT, pick whichever suits you better


# Financial support

This project has been made possible thanks to [Cocreators](https://cocreators.ee) and [Lietu](https://lietu.net). You can help us continue our open source work by supporting us on [Buy me a coffee](https://www.buymeacoffee.com/cocreators).

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/cocreators)
