"""
Detects red and blue colors from the camera. Also shows bounding box and confidence levels.
"""

# hi! to the unfortunate soul that has to read my code
# quick disclaimer: i dont use ai for things i cant write myself
# but i may use ai for things i know i can write myself
# oh yeah and for docs
# cant expect opencv devs to document their auto-generated python bindings
# and provide support directly inside vscode


import numpy as np
import argparse
import cv2

parser = argparse.ArgumentParser(
    prog = "Color Detector",
    description="Detects red and blue colors from the camera. Also shows bounding box and confidence levels.")

# 2. Add arguments
parser.add_argument("-wb", action="store_true", help="Enables white balance / color correction.")

# 3. Parse the arguments
args = parser.parse_args()
white_balance_enabled = args.wb

wb:cv2.xphoto.SimpleWB | None
if white_balance_enabled:
    wb = cv2.xphoto.createSimpleWB()
    print("White balance enabled.")
else:
    wb = None
    print("White balance disabled - append -wb to enable white balance.")

# in pixels, larger = less precise, more robust
fuzziness = 5

# Set range for red color
red_lower = np.array([136, 145, 111], np.uint8)
red_upper = np.array([180, 255, 255], np.uint8)
# since red crosses the hue boundary
red_lower_high = np.array([0, 145, 111], np.uint8)
red_upper_high = np.array([6, 255, 255], np.uint8)

# blue.
blue_lower = np.array([94, 145, 2], np.uint8)
blue_upper = np.array([120, 255, 255], np.uint8)



def draw_contours(img:cv2.typing.MatLike, contours, color_bgr:tuple, draw_string_template:str) -> None:
    """
    Draws contours and bounding boxes on the image in place.

    Use `{area}` to insert the area of the contour into draw_string_template.
    """

    # search up Non-Maximum Suppression if you are interested
    # i just want to merge boxes
    # NMSBoxes returns a list of indices of the contours to keep
    contours_idxs = cv2.dnn.NMSBoxes(
        [cv2.boundingRect(c) for c in contours],
        [cv2.contourArea(c) for c in contours], # score = area
        score_threshold=300, # reject areas below 300 px^2
        nms_threshold=1,  
    )


    for idx in contours_idxs:
        area = cv2.contourArea(contours[idx])
        x, y, w, h = cv2.boundingRect(contours[idx])
        # in-place modification of img
        img = cv2.rectangle(
            img, (x, y), (x + w, y + h), color_bgr, 2
        )
        # puts text on image
        cv2.putText(
            img,
            draw_string_template.format(area=area),
            (x, y-5), # or text will clip into the box
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color_bgr,
        )


# ---program start!---

print("Starting camera may take a few seconds, please wait...")
# takes like 5 seconds on my end, please wait patiently wawa :3
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_AUTO_WB, 1)

# mainloop
while cap.isOpened():
    # read frame
    ret, frame = cap.read()
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break

    # alter frame
    if wb:
        frame = wb.balanceWhite(frame)

    # for more intuitive color processing
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)


    # define mask
    red_mask = cv2.bitwise_or(cv2.inRange(hsv, red_lower, red_upper),cv2.inRange(hsv, red_lower_high, red_upper_high))
    blue_mask = cv2.inRange(hsv, blue_lower, blue_upper)

    # dilate detected pixels, make them bigger 
    kernel = np.ones((fuzziness, fuzziness), "uint8")
    red_mask = cv2.dilate(red_mask, kernel)
    res_red = cv2.bitwise_and(frame, frame, mask=red_mask)
    blue_mask = cv2.dilate(blue_mask, kernel)
    res_blue = cv2.bitwise_and(frame, frame, mask=blue_mask)

    # track red color
    red_contours, hierarchy = cv2.findContours(
        red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    draw_contours(frame, red_contours, (0, 0, 255), "Red (Area = {area} px²)",)

    # track blue color
    blue_contours, hierarchy = cv2.findContours(
        blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    draw_contours(frame, blue_contours, (255, 0, 0), "Blue (Area = {area} px²)",)
    
    
    # show the frame
    cv2.imshow("processed", frame)

    if cv2.waitKey(1) == ord("q"):
        break
    # close if exit button is pressed (shocking)
    if cv2.getWindowProperty("processed", cv2.WND_PROP_VISIBLE) < 1:
        break

# release everything if job is finished
cap.release()
cv2.destroyAllWindows()
