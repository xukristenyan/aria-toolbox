# Aria-Toolbox

A Python toolbox for connecting, streaming, visualizing, and recording from Project Aria Gen 1 glasses with built-in eye gaze inference.

## Installation

### Clone the repo

```bash
# With HTTP
git clone https://github.com/xukristenyan/aria-toolbox.git

# With SSH
git clone git@github.com:xukristenyan/aria-toolbox.git
```

### Install

#### Using uv
```bash
cd aria-toolbox
uv sync
```

#### Using conda
```bash
conda create -n aria python=3.10
conda activate aria
cd aria-toolbox
pip install -e .
```

## Usage

### Connect Your Device

Make sure your computer and the glasses are on the **same network**.

#### Using uv
```bash
# pair the glasses
uv run aria auth pair

# open the Aria app on the phone, click "Approve"

# click the Wi-Fi sign and get the device IP address of the glasses

# start streaming
uv run aria streaming start --interface wifi --device-ip YOUR_DEVICE_IP
```

#### Using conda
```bash
# pair the glasses
aria auth pair

# open the Aria app on the phone, click "Approve"

# click the Wi-Fi sign and get the device IP address of the glasses

# start streaming
aria streaming start --interface wifi --device-ip YOUR_DEVICE_IP
```

The inside LED faces the wearer and turns solid white when streaming begins.

### Examples

The toolbox is organized into a clear hierarchy of classes, where each level abstracts the complexity of the one below it.

- **`AriaGlasses`**: The low-level core class. It connects to the Aria device, subscribes to RGB and eye-tracking streams, runs on-device gaze inference, and provides thread-safe access to the latest state (RGB image, gaze coordinates).
    ```bash
    # stream data only (no viewer or recorder)
    uv run examples/stream_only.py          # using uv
    python examples/stream_only.py          # using conda
    ```

- **`Glasses`**: A high-level container that instantiates and coordinates one `AriaGlasses` object along with optional `Viewer` and `Recorder` modules. The `Viewer` renders frames with gaze overlays to the screen, while the `Recorder` writes RGB video, gaze-overlay video, and gaze data to disk.
    ```bash
    # live view with gaze overlay
    uv run examples/view_gaze.py            # using uv
    python examples/view_gaze.py            # using conda

    # live view + recording
    uv run examples/record_gaze.py          # using uv
    python examples/record_gaze.py          # using conda
    ```

### Default Configuration

You only need to include parameters that differ from the defaults.

```python
glasses_config = {
    "enable_viewer": False,             # set to True to see live streaming with gaze overlay
    "enable_recorder": False,           # set to True to record streams to disk

    "specifications": {
        "rgb_cam_res": [1408, 1408],
        "eye_cam_res": [240, 320],
        "gaze_depth": 1.0,
    },

    "viewer": {                         # configure if viewer is enabled
        "fps": 30,
    },

    "recorder": {                       # configure if recorder is enabled
        "fps": 10,
        "save_dir": "./recordings",
        "save_name": current_time,      # defaults to timestamp
        "auto_start": True,             # if False, press 's' to start recording manually
    },
}
```
