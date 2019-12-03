import datetime
import uuid
from PIL import Image
import ffmpeg
import os

import FileHandler


def extract_frames(source: str, folder: str, time: str, size: str, vframes: int, quality=15):
    uid = str(uuid.uuid4())

    ffmpeg.input(source, ss=str(datetime.timedelta(seconds=time))).output(folder + "\\" + uid + "_%d.jpg", s=size,
                                                                          vframes=vframes,
                                                                          qscale=quality).run(capture_stdout=True,
                                                                                              capture_stderr=True)

    return FileHandler.load_frames(uid, folder)


def compare_image(i1: str, i2: str):
    img1 = Image.open(i1)
    img2 = Image.open(i2)

    width = img1.size[0]
    height = img1.size[1]
    width1 = img2.size[0]
    height1 = img2.size[1]
    pix = img1.load()
    pix1 = img2.load()

    if width != width1 or height != height1:
        return None

    diff = 0
    for y in range(0, height, 12):
        for x in range(0, width, 12):
            diff += _pixel_diff(pix[x, y], pix1[x, y])

    maxDiff = 3 * 255 * width * height

    return 100.0 * diff / maxDiff


def same_image(image1: str, image2: str):
    if os.stat(image1).st_size != os.stat(image2).st_size:
        return False

    if compare_image(image1, image2) == 0.0:
        return True
    else:
        return False


def _pixel_diff(rgb1, rgb2):
    r1 = rgb1[0]
    g1 = rgb1[1]
    b1 = rgb1[2]
    r2 = rgb2[0]
    g2 = rgb2[1]
    b2 = rgb2[2]

    return abs(r1 - r2) + abs(g1 - g2) + abs(b1 - b2)
