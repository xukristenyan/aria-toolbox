import cv2
import time
from .utils.helpers import quit_keypress, draw_overlays


class Viewer:
    def __init__(self, config):
        self.fps = config["fps"]

        self.frame_interval = 1.0 / self.fps if self.fps > 0 else 0
        self.last_update_time = 0

        self.name = "View from Glasses"

        cv2.namedWindow(self.name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.name, 720, 720)

        self.viewer_alive = True


    def update(self, rgb_image, gaze):
        current_time = time.time()
        if current_time - self.last_update_time < self.frame_interval:
            return self.viewer_alive

        self.last_update_time = current_time

        rgb_image = draw_overlays(rgb_image, gaze)

        cv2.imshow(self.name, rgb_image)
       
        if quit_keypress() or cv2.getWindowProperty(self.name, cv2.WND_PROP_VISIBLE) < 1:
            cv2.destroyAllWindows()
            self.viewer_alive = False
            return self.viewer_alive

        return self.viewer_alive
