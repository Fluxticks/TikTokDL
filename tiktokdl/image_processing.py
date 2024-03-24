import cv2 as cv
from cv2 import Mat
import numpy as np
from urllib.request import urlopen

from typing import Tuple


def preprocess(image: Mat) -> Mat:
    """Preprocess a given image for better results in `find_position`.

    Args:
        image (Mat): The image to process.

    Returns:
        Mat: The resulting image after processing.
    """
    scale = 1
    delta = 0
    ddepth = cv.CV_16S

    output = cv.GaussianBlur(image, (3, 3), 0)
    output = cv.cvtColor(output, cv.COLOR_BGR2GRAY)
    gradient_x = cv.Sobel(
        output,
        ddepth,
        1,
        0,
        ksize=3,
        scale=scale,
        delta=delta,
        borderType=cv.BORDER_DEFAULT,
    )
    gradient_y = cv.Sobel(
        output,
        ddepth,
        0,
        1,
        ksize=3,
        scale=scale,
        delta=delta,
        borderType=cv.BORDER_DEFAULT,
    )

    gradient_x_abs = cv.convertScaleAbs(gradient_x)
    gradient_y_abs = cv.convertScaleAbs(gradient_y)
    gradient = cv.addWeighted(gradient_x_abs, 0.5, gradient_y_abs, 0.5, 0)

    return gradient


def image_from_url(url: str) -> Mat:
    """Load an image from a URL.

    Args:
        url (str): A URL to an image.

    Returns:
        Mat: The image object of the given URL.
    """
    image_request = urlopen(url)
    image_array = np.asarray(bytearray(image_request.read()), dtype=np.uint8)
    return cv.imdecode(image_array, -1)


def find_position(
    background_image: Mat, piece_image: Mat, method: int = cv.TM_SQDIFF
) -> Tuple[int, int]:
    """For a given puzzle piece image, find it's corresponding position in the background image.

    Args:
        background_image (Mat): The background image to find the position in.
        piece_image (Mat): The puzzle piece to match the location of.
        method (int, optional): The matching method to use. Defaults to cv.TM_SQDIFF.

    Returns:
        tuple[int, int]: The (x,y) position of the top left corner of the matched position.
    """

    sobel_bg = preprocess(background_image)
    sobel_piece = preprocess(piece_image)

    coordinates_found = cv.matchTemplate(sobel_bg, sobel_piece, method)
    _, _, min_loc, max_loc = cv.minMaxLoc(coordinates_found)
    if method in (cv.TM_SQDIFF, cv.TM_SQDIFF_NORMED):
        return min_loc
    else:
        return max_loc
