import os.path
from copy import deepcopy

import cv2
import numpy as np
import pyrealsense2 as rs


class CaptureMulVideo:
    def __init__(self, save_dir):
        # camera setting
        self.connected_devices = []

        # save setting
        self.save_dir = save_dir
        self.stop_key = ord('s')
        self.quit_key = ord('q')
        self.capture_key = ord('c')
        self.save_count = 0
        self.capture_count = 0

        self.recording = False
        self.out = None
        self.check_dir()

        self.image_save_name_1 = ""
        self.image_save_name_2 = ""
        self.save_name_1 = f"capture_top_{self.save_count}.avi"
        self.save_name_2 = f"capture_side_{self.save_count}.avi"

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
        realsense_ctx = rs.context()
        devices = realsense_ctx.query_devices()
        for dev in devices:
            dev.hardware_reset()

        for i in range(len(realsense_ctx.devices)):
            detected_camera = realsense_ctx.devices[i].get_info(rs.camera_info.serial_number)
            self.connected_devices.append(detected_camera)

    def camera_pipeline(self, device_name):
        pipeline = rs.pipeline()
        config = rs.config()

        config.enable_device(device_name)
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

        return pipeline, config

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

    def video_recoder(self, name):
        save_path = os.path.join(self.save_dir, name)
        out = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*'XVID'), 60, (640, 480))
        return out

    def start_streaming(self):
        object_num = 2
        count = 0
        self.initialize_camera()
        pipeline1, config1 = self.camera_pipeline(self.connected_devices[0])
        pipeline2, config2 = self.camera_pipeline(self.connected_devices[1])

        pipeline1.start(config1)
        pipeline2.start(config2)

        out_1 = self.video_recoder(name=self.save_name_1)
        out_2 = self.video_recoder(name=self.save_name_2)

        print("\n\n\n")
        print("Start Streaming. \nIf you want to save a video, press s")
        print("If you want to save an image, press c")
        print("If you want to quit streaming, press q")
        print("\n\n\n")

        try:
            while True:
                color1, depth1, cs1 = self.capture_pipeline(pipeline=pipeline1)
                color2, depth2, cs2 = self.capture_pipeline(pipeline=pipeline2)
                if cs1 or cs2:
                    continue

                # show center of image
                view_color1 = deepcopy(color1)
                view_color2 = deepcopy(color2)
                cv2.circle(view_color1, (320, 240), 5, (0, 0, 255), -1)
                cv2.circle(view_color2, (320, 240), 5, (0, 0, 255), -1)

                images1 = np.hstack((view_color1, view_color2))
                # images2 = np.hstack((depth1, depth2))
                # images = np.vstack((images1, images2))
                out_1.write(color1)
                out_2.write(color2)
                cv2.imshow('RealSense', images1)
                # cv2.imshow("Two Images", images)

                key = cv2.waitKey(1) & 0xFF
                if key == self.capture_key:
                    # save images
                    self.capture_count += 1
                    self.image_save_name_1 = f"capture_cam1_{self.capture_count}.png"
                    self.image_save_name_2 = f"capture_cam2_{self.capture_count}.png"
                    cv2.imwrite(os.path.join(self.save_dir, self.image_save_name_1), color1)
                    cv2.imwrite(os.path.join(self.save_dir, self.image_save_name_2), color2)
                    print(f"Save image, save count = {self.capture_count}\n")

                if key == self.stop_key:
                    if self.recording:
                        if out_1 is not None:
                            out_1.release()
                            out_2.release()
                            print(f"Recording stopped, save count = {self.save_count}\n")

                        self.recording = False
                        self.save_count += 1
                        self.save_name_1 = f"capture_cam1_{self.save_count}.avi"
                        self.save_name_2 = f"capture_cam2_{self.save_count}.avi"

                    else:
                        self.recording = True
                        out_1 = self.video_recoder(name=self.save_name_1)
                        out_2 = self.video_recoder(name=self.save_name_2)
                        print(f"Recording started, save count = {self.save_count}")

                if self.recording:
                    out_1.write(color1)
                    out_2.write(color2)

                if key == self.quit_key:
                    print(f"Quit, total save count = {self.save_count}\n")
                    break

        finally:
            pipeline1.stop()
            pipeline2.stop()
            if out_1 is not None:
                out_1.release()
                out_2.release()

            cv2.destroyAllWindows()
