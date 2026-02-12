import time
from .aria_gen1 import AriaGlasses
from .viewer import Viewer
from .recorder import Recorder
from .utils.helpers import start_keypress, end_keypress


class Glasses:

    def __init__(self, device_ip, config):
        self.device_ip = device_ip

        aria_config = config.get("specifications", {})
        self.aria_glasses = AriaGlasses(self.device_ip, aria_config)

        if config.get("enable_viewer", True):
            conf = config.get("viewer", {})
            viewer_config = {
                "fps": conf.get("fps", 30)
            }
            self.viewer = Viewer(viewer_config)
        else:
            self.viewer = None

        if config.get("enable_recorder", False):
            conf = config.get("recorder", {})
            save_time = time.strftime("%Y%m%d_%H%M%S")
            recorder_config = {
                "save_dir": conf.get("save_dir", "./recordings"),
                "save_name": conf.get("save_name", f"{save_time}"),
                "fps": conf.get("fps", 10),
            }
            self.recorder = Recorder(recorder_config)
            self.auto_start = conf.get("auto_start", True)
        else:
            self.recorder = None

        self.is_alive = False
        self.recording_started = False

        self.state = {"timestamp": None, "rgb_image": None, "gaze": None}


    def launch(self):
        self.aria_glasses.launch()
        self.is_alive = True


    def update(self):
        if self.is_alive:
            state = self.aria_glasses.get_current_state()
            self.state.update(state)

            if self.state["rgb_image"] is not None:

                if self.recorder:
                    if not self.recording_started:
                        if self.auto_start:
                            self.recording_started = True
                            print(f"[Glasses Recorder] Recording started !!!")

                        elif start_keypress():
                            self.recording_started = True
                            print(f"[Glasses Recorder] Recording started !!!")

                    if self.recording_started:
                        # to be updated
                        self.recorder.update(self.state["rgb_image"], self.state["gaze"])

                        if end_keypress():
                            self.recording_started = False
                            print(f"[Glasses Recorder] Recording stopped !!!")

                if self.viewer:
                    self.viewer.update(self.state["rgb_image"], self.state["gaze"])
                    if not self.viewer.viewer_alive:
                        self.is_alive = False

        else:
            self.shutdown()

        return self.state


    def get_current_state(self):
        return self.state


    def shutdown(self):
        if self.recorder:
            self.recorder.stop()
        self.aria_glasses.shutdown()
