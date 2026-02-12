from aria_toolbox import AriaGlasses

device_ip = "xxx.xxx.xxx.xxx"       # TODO: replace with your glasses' IP address

glasses_config = {      # you can leave the dict empty if using default parameter settings
    "rgb_cam_res": [1408, 1408],
    "eye_cam_res": [240, 320],
    "gaze_depth": 1.0
}

def main():
    aria = None

    try:
        aria = AriaGlasses(device_ip, glasses_config)
        aria.launch()

        while True:
            state = aria.get_current_state()

    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Exiting gracefully.")

    except Exception as e:
        print(f"Unexpected error occurred: {e}")

    finally:
        if aria:
            aria.shutdown()



if __name__ == "__main__":
    main()