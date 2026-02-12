from aria_toolbox import Glasses


device_ip = "xxx.xxx.xxx.xxx"       # TODO: replace with your glasses' IP address

glasses_config = {
    "enable_viewer": True,

    "specifications": {             # you can leave the dict empty if using default parameter settings
        "rgb_cam_res": [1408, 1408],
        "eye_cam_res": [240, 320],
        "gaze_depth": 1.0
    },

    "viewer": {                     # no need to keep this dict if "enable_viewer" is False
        "fps": 30
    },

}

def main():
    glasses = None

    try:
        glasses = Glasses(device_ip, glasses_config)

        glasses.launch()

        while True:
            state = glasses.update()

            if not glasses.is_alive:
                break

    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Exiting gracefully.")

    except Exception as e:
        print(f"Unexpected error occurred: {e}")

    finally:
        if glasses:
            glasses.shutdown()



if __name__ == "__main__":
    main()