import numpy as np
import cv2
import collections
import subprocess
import os
import datetime

Box = collections.namedtuple('Box', 'left top width height')
RGB = collections.namedtuple('RGB', 'red green blue')
# Point = collections.namedtuple('Point', 'x y')


def screenshot(image_name=None, region=None):
    if image_name is None:
        tmp_filename = f"screenshot{(datetime.datetime.now().strftime('%Y-%m%d_%H-%M-%S-%f'))}.png"
    else:
        tmp_filename = image_name
    if region is None:
        subprocess.run(['screencapture', '-x', tmp_filename])
        im = cv2.imread(tmp_filename)
    else:
        subprocess.run(['screencapture', '-x', "-R", f"{region[0]//2},{region[1]//2},{region[2]//2+1},{region[3]//2+1}", tmp_filename])
        im = cv2.imread(tmp_filename)
        im = im[region[1] % 2:region[1] % 2 + region[3], region[0] % 2:region[0] % 2 + region[2], :]

    if image_name is None:
        os.unlink(tmp_filename)
    return im


def locate_all(needle_image, haystack_image, limit=10000, confidence=0.999):

    needle_height, needle_width = needle_image.shape[:2]

    if (haystack_image.shape[0] < needle_image.shape[0] or haystack_image.shape[1] < needle_image.shape[1]):
        # avoid semi-cryptic OpenCV error below if bad size
        raise ValueError('needle dimension(s) exceed the haystack image or region dimensions')

    # get all matches at once, credit: https://stackoverflow.com/questions/7670112/finding-a-subimage-inside-a-numpy-image/9253805#9253805
    result = cv2.matchTemplate(haystack_image, needle_image, cv2.TM_CCOEFF_NORMED)
    match_indices = np.arange(result.size)[(result > confidence).flatten()]
    matches = np.unravel_index(match_indices[:limit], result.shape)

    if len(matches[0]) == 0:
        return

    # use a generator for API consistency:
    matchx = matches[1]  # vectorized
    matchy = matches[0]
    # return matchx, matchy, needle_width, needle_height
    for x, y in zip(matchx, matchy):
        yield Box(x, y, needle_width, needle_height)


def locate_all_on_screen(im_name, region=None, confidence=0.999):
    needle_image = cv2.imread(im_name)
    haystack_image = screenshot(region=region)
    relative_results = tuple(locate_all(needle_image, haystack_image, confidence=confidence))
    absolute_results = []
    if region is None:
        region = (0, 0, 0, 0)
    for result in relative_results:
        absolute_results.append(Box(result[0] + region[0], result[1] + region[1], result[2], result[3]))
    return absolute_results


def locate_on_screen(im_name, region=None, confidence=0.999):
    results = locate_all_on_screen(im_name, region, confidence)
    return results[0] if len(results) > 0 else None


def pixel_match_color(x, y, expected_RGB_color, tolerance=0):
    pix = screenshot(region=(x, y, 1, 1))[0, 0, ::-1]
    assert len(expected_RGB_color) == 3
    expected = np.array(expected_RGB_color)
    return (np.abs(pix - expected) < tolerance).all()


# if __name__ == '__main__':
#     pass