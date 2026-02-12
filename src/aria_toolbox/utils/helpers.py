import cv2


def quit_keypress():
    key = cv2.waitKey(1)
    # press ESC
    return key == 27


def start_keypress():
    key = cv2.waitKey(1)
    # press s
    return key == ord('s')


def end_keypress():
    key = cv2.waitKey(1)
    # press e
    return key == ord('e')


def draw_overlays(image, gaze):
    copied = image.copy()

    if gaze is not None:
        cv2.circle(copied, (int(gaze[0]), int(gaze[1])), 5, (0, 255, 0), 10)

    return copied

