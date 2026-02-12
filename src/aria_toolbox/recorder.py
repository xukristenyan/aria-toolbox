import cv2
import os
import time
import numpy as np
from .utils.helpers import draw_overlays


class Recorder:
    '''
    Records video streams from a camera in mp4:
        - rgb stream
        - rgb stream with gaze overlays
    '''
    def __init__(self, config):
        self.save_dir = config["save_dir"]
        self.save_name = config["save_name"]
        self.fps = config["fps"]

        self.frame_interval = 1.0 / self.fps if self.fps > 0 else 0
        self.last_update_time = 0

        self.plain_writer = None
        self.overlay_writer = None
        self.gaze_writer = None
        self.is_recording = False

        self.session_dir = os.path.join(self.save_dir, self.save_name)
        os.makedirs(self.session_dir, exist_ok=True)
        
        print(f"[Glasses Recorder] Ready to record.")


    def _initialize_writers(self, rgb_image):
        height, width, _ = rgb_image.shape
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        plain_path = os.path.join(self.session_dir, "aria_rgb.mp4")
        self.plain_writer = cv2.VideoWriter(plain_path, fourcc, self.fps, (width, height))

        overlay_path = os.path.join(self.session_dir, "aria_rgb_gaze.mp4")
        self.overlay_writer = cv2.VideoWriter(overlay_path, fourcc, self.fps, (width, height))

        self.gaze_path = os.path.join(self.session_dir, "aria_gaze.npy")
        self.gazes = []
        self.count = 0

        self.is_recording = True


    def update(self, rgb_image, gaze):
        current_time = time.time()
        if current_time - self.last_update_time < self.frame_interval:
            return True
        self.last_update_time = current_time

        if not self.is_recording:
            self._initialize_writers(rgb_image)

        if self.plain_writer:
            self.plain_writer.write(rgb_image)

        if self.overlay_writer:
            overlay_image = draw_overlays(rgb_image, gaze)
            self.overlay_writer.write(overlay_image)

        if gaze is None:
            gaze = np.array([np.nan, np.nan], dtype=float)
        self.gazes.append((self.count, gaze))
        self.count += 1


    def stop(self):
        if self.is_recording:
            if self.plain_writer:
                self.plain_writer.release()

            if self.overlay_writer:
                self.overlay_writer.release()

            np.save(self.gaze_path, np.array(self.gazes, dtype=object))
            
            self.is_recording = False

            print(f"[Glasses Recorder] recordings are saved in: {self.session_dir}")
