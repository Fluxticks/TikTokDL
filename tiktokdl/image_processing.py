import cv2 as cv
from cv2 import Mat
import numpy as np
from urllib.request import urlopen


def preprocess(image: Mat) -> Mat:
    scale = 1
    delta = 0
    ddepth = cv.CV_16S

    output = cv.GaussianBlur(image, (3, 3), 0)
    output = cv.cvtColor(output, cv.COLOR_BGR2GRAY)
    gradient_x = cv.Sobel(output, ddepth, 1, 0, ksize=3, scale=scale, delta=delta, borderType=cv.BORDER_DEFAULT)
    gradient_y = cv.Sobel(output, ddepth, 0, 1, ksize=3, scale=scale, delta=delta, borderType=cv.BORDER_DEFAULT)

    gradient_x_abs = cv.convertScaleAbs(gradient_x)
    gradient_y_abs = cv.convertScaleAbs(gradient_y)
    gradient = cv.addWeighted(gradient_x_abs, 0.5, gradient_y_abs, 0.5, 0)

    return gradient


def image_from_url(url: str) -> Mat:
    image_request = urlopen(url)
    image_array = np.asarray(bytearray(image_request.read()), dtype=np.uint8)
    return cv.imdecode(image_array, -1)


def find_position(background_image: Mat, piece_image: Mat, method: int = cv.TM_SQDIFF) -> tuple[int, int]:
    sobel_bg = preprocess(background_image)
    sobel_piece = preprocess(piece_image)

    coordinates_found = cv.matchTemplate(sobel_bg, sobel_piece, method)
    _, _, min_loc, max_loc = cv.minMaxLoc(coordinates_found)
    if method in (cv.TM_SQDIFF, cv.TM_SQDIFF_NORMED):
        return min_loc
    else:
        return max_loc