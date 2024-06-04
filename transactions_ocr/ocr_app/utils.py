# USAGE
# python match.py -i image.jpg -o crop.jpg -t logo.png -v y

# import the necessary packages
import numpy as np
import argparse
import imutils
import cv2
import os
import datetime
from pathlib import Path

def match_logo( input_image_path, min_scale=0.1, max_scale=3, number_of_scales=100):
    min_scale = 0.1
    max_scale = 3
    number_of_scales = 100
    cropped_image_folder = 'media/temp/cropped_temp'
    LOGO_PATH = 'media/temp/logos'
    for logo_image_path in  os.listdir(LOGO_PATH):
        print(min_scale, max_scale, number_of_scales)
        # load the image image, convert it to grayscale, and detect edges
        file_path_str = Path(LOGO_PATH, logo_image_path)
        template = cv2.imread(str(file_path_str))
        template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        template = cv2.Canny(template, 50, 200)
        (tH, tW) = template.shape[:2]


        # load the image, convert it to grayscale, and initialize the
        # bookkeeping variable to keep track of the matched region
        image = cv2.imread(str(input_image_path))
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        found = None

        # loop over the scales of the image
        for scale in np.linspace(min_scale, max_scale, number_of_scales)[::-1]:
            # resize the image according to the scale, and keep track
            # of the ratio of the resizing
            resized = imutils.resize(gray, width=int(gray.shape[1] * scale))
            r = gray.shape[1] / float(resized.shape[1])

            # if the resized image is smaller than the template, then break
            # from the loop
            if resized.shape[0] < tH or resized.shape[1] < tW:
                break

            # detect edges in the resized, grayscale image and apply template
            # matching to find the template in the image
            edged = cv2.Canny(resized, 50, 200)
            result = cv2.matchTemplate(edged, template, cv2.TM_CCOEFF)
            (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)


            # if we have found a new maximum correlation value, then ipdate
            # the bookkeeping variable
            if found is None or maxVal > found[0]:
                found = (maxVal, maxLoc, r)

        # unpack the bookkeeping varaible and compute the (x, y) coordinates
        # of the bounding box based on the resized ratio
        (_, maxLoc, r) = found
        (startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
        (endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))


        # if args.get("visualize", False):
        #     cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)
        #     cv2.imshow("Image", image)
        #     cv2.waitKey(0)

        cropped_image = image[startY:endY, startX:endX]
        current_date_time = datetime.datetime.now()
        date_time_str = current_date_time.strftime("%Y_%m_%d_%H_%M_%S")
        success =cv2.imwrite(f'{cropped_image_folder}/_cropped_{date_time_str}.jpg', cropped_image)
        print(success, 'images cropped successfully!')