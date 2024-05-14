# Simple Video and Photo Capture with PyRealSense & OpenCV

This project is a Python code that utilizes Intel RealSense camera and OpenCV to capture videos and photos with simple key events. It also provides a GUI that manually saves videos in frame units.


## I. Multi-Camera/Single-Camera Capture
### Usage
1. Clone the project.

   ```bash
   git clone https://github.com/ChoRongCho/pyrealsense_multicam.git
   ```

2. Install the necessary dependencies.

   ```bash
   pip install pyrealsense2 opencv-python
   ```

3. Run `main.py`.

   ```bash
   python main.py
   ```

4. You can record videos or take photos using simple keyboard events.

### Support

Currently, this code supports the following functionalities:

- "s" : Frame Change
- "c" : Capture a photo
- "q" : Quit the RealSense application

### Dependencies

- pyrealsense2
- opencv-python

## II. Frame Extraction
### Usage
1. Clone the project.

   ```bash
   git clone https://github.com/ChoRongCho/pyrealsense_multicam.git
   ```

2. Install the necessary dependencies.

   ```bash
   pip install tk opencv-python pillow
   ```

3. Edit `main.py`.

   ```python
   if __name__ == "__main__":
      # main()        <-----X
      extract_video() <-----O
   ```

4. You can capture a video using simple keyboard events.

### Support

Currently, this code supports the following functionalities:

- "Right" : Frame Change +1 
- "Left" : Frame Change -1
- "Up" : Frame Change +10
- "Down" : Frame Change -10
- "period . " : Frame Change +100
- "comma , " : Frame Change -100
- "Escape" : Quit program 
- "Space" : Save a frame

### Dependencies

- thinter
- PIL
- opencv-python



## III. License

This code is distributed under the MIT License. For more information, refer to the LICENSE file.