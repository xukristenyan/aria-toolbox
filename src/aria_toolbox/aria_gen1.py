
from .utils import mute_warning
from .utils.connection import update_iptables
import sys
import torch
import aria.sdk as aria
import threading
import numpy as np
import time
from importlib import resources
from .gaze_inference import infer

from projectaria_tools.core.calibration import device_calibration_from_json_string, get_linear_camera_calibration
from projectaria_tools.core.mps.utils import get_gaze_vector_reprojection
from projectaria_tools.core.mps import EyeGaze


class AriaGlasses:
    def __init__(self, device_ip, config: dict):
        self.device_ip = device_ip
        self.rgb_cam_res = config.get('rgb_cam_res', [1408, 1408])
        self.eye_cam_res = config.get('eye_cam_res', [240, 320])
        self.gaze_depth = config.get('gaze_depth', 1.0)

        if sys.platform.startswith("linux"):
            update_iptables()

        aria.set_log_level(aria.Level.Info)
        self._setup_gaze_inference()

        self.connected = False
        self.stream_active = False
        self.record_active = False
        self.gaze = None
        self.eye_gaze = None

        self.state = {
            "timestamp": time.time(),
            "rgb_image": None,
            "gaze": None,
        }


    def _setup_gaze_inference(self):
        base = resources.files("aria_toolbox") / "gaze_inference" / "model" / "pretrained_weights"

        model_weights = base / "weights.pth"
        model_config = base / "config.yaml"

        self.model_device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.gaze_model = infer.EyeGazeInference(str(model_weights), str(model_config), self.model_device)

        torch.set_num_threads(1)


    def _get_calibration(self, streaming_manager):
        sensors_calib_json = streaming_manager.sensors_calibration()
        self.device_calibration = device_calibration_from_json_string(sensors_calib_json)

        self.rgb_camera_calib = self.device_calibration.get_camera_calib('camera-rgb')
        self.rgb_dist_calib = get_linear_camera_calibration(512, 512, 150, 'camera-rgb')


    def launch(self):
        # connect to Aria glasses
        try:
            self.device_client = aria.DeviceClient()
            client_config = aria.DeviceClientConfig()
            
            client_config.ip_v4_address = self.device_ip
            self.device_client.set_client_config(client_config)
            self.device = self.device_client.connect()
            
            self.connected = True
            print(f"[AriaGlasses] Connected!")

        except Exception as e:
            self.connected = False
            print(f"[AriaGlasses] Failed to connect: {e}!")

        # start streaming
        try:
            streaming_manager = self.device.streaming_manager            
            self._get_calibration(streaming_manager)

            self.streaming_client = aria.StreamingClient()

            # update subscription config
            subs_config = self.streaming_client.subscription_config

            ## subscribe to specified streams
            self.data_types = ['rgb', 'et']
            subs_config.subscriber_data_type = (aria.StreamingDataType.Rgb | aria.StreamingDataType.EyeTrack)

            ## set message queue size
            subs_config.message_queue_size[aria.StreamingDataType.Rgb] = 1
            subs_config.message_queue_size[aria.StreamingDataType.EyeTrack] = 1

            ## set security options
            options = aria.StreamingSecurityOptions()
            options.use_ephemeral_certs = True
            subs_config.security_options = options

            self.streaming_client.subscription_config = subs_config

            # create and attach observer
            self._observer = _Observer()
            self.streaming_client.set_streaming_client_observer(self._observer)

            # start listening
            self.streaming_client.subscribe()
            self.stream_active = True
            print("[AriaGlasses] Streaming starts!")

        except Exception as e:
            self.stream_active = False
            print(f"[AriaGlasses] Failed to start streaming: {e}")


    def shutdown(self):
        if self.stream_active:
            try:
                self.streaming_client.unsubscribe()
                self.stream_active = False

            except Exception as e:
                print(f"[AriaGlasses] Failed to shut down: {e}")


    def get_current_state(self):
        if not self.stream_active:
            return

        raw_images = self._observer.take()

        rgb_raw = raw_images.get(aria.CameraId.Rgb)
        et_raw = raw_images.get(aria.CameraId.EyeTrack)

        # process RGB: rotate 90° CW, BGR→RGB, if RGB frame is available
        rgb_image = None
        if rgb_raw is not None:
            rgb_image = np.rot90(rgb_raw, -1)
            rgb_image = rgb_image[:, :, ::-1].copy()

        # compute gaze if ET frame is available
        gaze = None
        if et_raw is not None:
            gaze = self._compute_gaze(et_raw)

        self.state = {
            "timestamp": time.time(),
            "rgb_image": rgb_image,
            "gaze": gaze,
        }

        return self.state


    def _compute_gaze(self, et_image):
        et_image = torch.tensor(et_image)

        if np.median(et_image) < 10:
            return None

        try:
            with torch.no_grad():
                preds, _, _ = self.gaze_model.predict(et_image)
                preds = preds.detach().cpu().numpy()

            eye_gaze = EyeGaze
            eye_gaze.yaw = preds[0][0]
            eye_gaze.pitch = preds[0][1]

            projection = get_gaze_vector_reprojection(
                eye_gaze,
                'camera-rgb',
                self.device_calibration,
                self.rgb_camera_calib,
                self.gaze_depth,
            )

            if projection.any() is None:
                return None
            
            x, y = projection
            rotated_x = self.rgb_cam_res[0] - y
            rotated_y = x

            return np.array([rotated_x, rotated_y], dtype=np.float32)

        except Exception:
            return None


class _Observer:
    def __init__(self):
        self._lock = threading.Lock()
        self._raw_images = {}

    def on_image_received(self, image, record):
        with self._lock:
            self._raw_images[record.camera_id] = image
    
    def take(self):
        with self._lock:
            return self._raw_images.copy()