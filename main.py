from script.capture_streaming import CaptureVideo
from script.multicamera_capture import CaptureMulVideo

def main():
    save_dir = "./data2/obj"
    cap_video = CaptureMulVideo(save_dir=save_dir)

    cap_video.start_streaming()


if __name__ == '__main__':
    main()