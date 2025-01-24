import cv2
import numpy
import base64
import os
from datetime import datetime

def find_flower_cv(b64img: str) -> str:
    """
    :param b64img: Base64 encoded image string (image string part only).
    :return: Base64 encoded processed image string (image string part only).
    """

    # decode the Base64 image to an OpenCV  format
    image_array = numpy.frombuffer(base64.b64decode(b64img), numpy.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError("Failed to decode image from Base64 input.")

    # process the image and get coordinates
    processed_image, normalized_coords = detect_flowers_and_simplify(image)

    # check and make directories
    # os.makedirs("cv_processed_img", exist_ok=True)

    # make a timestamped file name
    # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # filename = f"cv_processed_img/processed_image_{timestamp}"

    # save the processed image
    # image_path = f"{filename}.png"
    # cv2.imwrite(image_path, processed_image)

    # save coordinates to a text
    # txt_path = f"{filename}.txt"
    # with open(txt_path, "w") as f:
    #     for coord in normalized_coords:
    #         f.write(f"{coord[0]:.6f}, {coord[1]:.6f}\n")

    # convert processed image to Base64
    _, buffer = cv2.imencode(".png", processed_image)
    result_base64 = base64.b64encode(buffer).decode("utf-8")

    return result_base64


def detect_flowers_and_simplify(image, output_size=(500, 500)):
    """
    :return: (processed_image, normalized_coordinates).
    """

    image_resized = cv2.resize(image, output_size)
    height, width, _ = image_resized.shape

    # convert to HSV
    hsv_image = cv2.cvtColor(image_resized, cv2.COLOR_BGR2HSV)

    # mask for white like colors (flowers)
    lower_white = numpy.array([0, 0, 200])
    upper_white = numpy.array([180, 30, 255])
    mask = cv2.inRange(hsv_image, lower_white, upper_white)

    # detect contours of the flowers
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # create output image
    output_image = numpy.zeros_like(image_resized)
    normalized_coords = []

    for contour in contours:
        # get the center of each flower
        moment = cv2.moments(contour)
        if moment["m00"] != 0:
            cx = int(moment["m10"] / moment["m00"])
            cy = int(moment["m01"] / moment["m00"])

            # normalize coordinates
            normalized_coords.append((cx / width, cy / height))

            # draw a white circle to represent the flower location
            cv2.circle(output_image, (cx, cy), 10, (255, 255, 255), -1)

    return output_image, normalized_coords
