import os.path

import cv2
import numpy as np
import pyrealsense2 as rs


class CaptureVideo:
    def __init__(self, save_dir):
        self.save_dir = save_dir
        self.stop_key = ord('s')
        self.quit_key = ord('q')
        self.save_count = 0

        self.recording = False
        self.out = None
        self.save_name = f"capture_{self.save_count}.avi"

        # camera info
        self.pp, self.ff = 0.0, 0.0
        self.device_product_line = None

    def setting_init(self):
        pipeline = rs.pipeline()
        config = rs.config()

        # Get device product line for setting a supporting resolution
        pipeline_wrapper = rs.pipeline_wrapper(pipeline)
        pipeline_profile = config.resolve(pipeline_wrapper)
        device = pipeline_profile.get_device()
        self.device_product_line = str(device.get_info(rs.camera_info.product_line))

        found_rgb = False
        for s in device.sensors:
            if s.get_info(rs.camera_info.name) == 'RGB Camera':
                found_rgb = True
                break
        if not found_rgb:
            print("The demo requires Depth camera with Color sensor")
            exit(0)

        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 60)
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 60)

        cfg = pipeline.start(config)
        profile = cfg.get_stream(rs.stream.color)
        intr = profile.as_video_stream_profile().get_intrinsics()

        # get intrinsic parameter
        self.pp = (intr.ppx, intr.ppy)
        self.ff = (intr.fx, intr.fy)
        return pipeline

    def video_recoder(self, w=640, h=480):
        save_path = os.path.join(self.save_dir, self.save_name)
        out = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*'XVID'), 0, (w, h))
        return out

    def start_streaming(self):
        pipeline = self.setting_init()
        out = self.video_recoder()
        print("Start Streaming. If you want to start save a video, press s")

        try:
            while True:

                frames = pipeline.wait_for_frames()
                color_frame = frames.get_color_frame()
                color_image = np.asanyarray(color_frame.get_data())
                out.write(color_image)
                cv2.imshow('Realsense', color_image)

                key = cv2.waitKey(1) & 0xFF
                if key == self.stop_key:
                    if self.recording:
                        if out is not None:
                            out.release()
                            print(f"Recording stopped, save count = {self.save_count}\n")

                        self.recording = False
                        self.save_count += 1
                        self.save_name = f"capture_{self.save_count}.avi"

                    else:
                        self.recording = True
                        out = self.video_recoder()
                        print(f"Recording started, save count = {self.save_count}")

                if self.recording:
                    out.write(color_image)
                if key == self.quit_key:
                    print(f"Quit, total save count = {self.save_count}\n")
                    break

        finally:
            pipeline.stop()
            if out is not None:
                out.release()
            cv2.destroyAllWindows()


