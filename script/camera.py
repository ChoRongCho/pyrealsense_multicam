import os.path

import cv2
import numpy as np
import pyrealsense2 as rs


class MulCamera:
    def __init__(self, save_dir) -> None:    
    # camera setting
        self.connected_devices = []

        # save setting
        self.save_dir = save_dir
        self.stop_key = ord('s')
        self.quit_key = ord('q')
        self.save_count = 0

        self.recording = False
        self.out = None
        self.save_name_1 = f"capture_top_{self.save_count}.avi"
        self.save_name_2 = f"capture_side_{self.save_count}.avi"

        # camera info
        self.pp, self.ff = 0.0, 0.0
        self.device_product_line = None
    
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
        depth_colormap= cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.5), cv2.COLORMAP_JET)
        return color_image, depth_colormap, continue_sig