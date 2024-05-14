from script.extract_frame import *
from script.multicamera_capture import CaptureMulVideo


def extract_video():
    root = tk.Tk()
    app = VideoToFramesGUI(root,
                           video_path="data/scene1/SuperShy.mp4",
                           name="NewJeans",
                           save_dir="./result/scene1")
    root.mainloop()


def main():
    save_dir = "./data/scene1"
    cap_video = CaptureMulVideo(save_dir=save_dir)
    cap_video.start_streaming()


if __name__ == '__main__':
    # main()
    extract_video()
