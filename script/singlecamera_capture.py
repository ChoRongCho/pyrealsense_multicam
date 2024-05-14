import os.path
from copy import deepcopy
import cv2
import numpy as np
import pyrealsense2 as rs


class CaptureVideo:
    def __init__(self, save_dir):
        self.save_dir = save_dir
        self.stop_key = ord('s')
        self.quit_key = ord('q')
        self.capture_key = ord('c')
        self.save_count = 0
        self.capture_count = 0

        self.check_dir()
        self.recording = False
        self.out = None
        self.image_save_name = ""
        self.video_save_name = ""

        # camera info
        self.pp, self.ff = 0.0, 0.0
        self.device_product_line = None

    def check_dir(self):
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
            print(f"{self.save_dir} created. ")
        else:
            print(f"{self.save_dir} already exists. ")

    def initialize_camera(self):
        pipeline = rs.pipeline()
        config = rs.config()

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
    
    def capture_pipeline(self, pipeline):
        # Wait for a coherent pair of frames: depth and color
        continue_sig = 0
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame or not color_frame:
            continue_sig = 1
            return continue_sig

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.5), cv2.COLORMAP_JET)
        return color_image, depth_colormap, continue_sig

    def video_recoder(self, w=640, h=480):
        save_path = os.path.join(self.save_dir, self.video_save_name)
        out = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*'XVID'), 0, (w, h))
        return out

    def start_streaming(self):
        pipeline = self.initialize_camera()
        out = self.video_recoder()
        print("Start Streaming. If you want to start save a video, press s")

        try:
            while True:
                color_image, depth_image, cs = self.capture_pipeline(pipeline=pipeline)
                if cs:
                    continue

                # show center of image
                view_color = deepcopy(color_image)
                cv2.circle(view_color, (320, 240), 5, (0, 0, 255), -1)
                # hstack_image = np.hstack((view_color, depth_image))
                # vstack_image = np.vstack((view_color, depth_image))

                # video write
                out.write(color_image)

                # Show Images
                # cv2.imshow("V Image", vstack_image)
                # cv2.imshow("H Image", hstack_image)
                cv2.imshow('Realsense', color_image)

                key = cv2.waitKey(1) & 0xFF
                if key == self.capture_key:
                    self.capture_count += 1
                    self.image_save_name = f"capture_top_{self.capture_count}.png"
                    cv2.imwrite(os.path.join(self.save_dir, self.image_save_name), color_image)
                    print(f"Save image, save count = {self.capture_count}\n")
                    
                if key == self.stop_key:
                    if self.recording:
                        if out is not None:
                            out.release()
                            print(f"Recording stopped, save count = {self.save_count}\n")

                        self.recording = False
                        self.save_count += 1
                        self.video_save_name = f"capture_{self.save_count}.avi"

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


