# Visually Impaired Assistant - Object Detection App

This application uses Kivy for the user interface, OpenCV for camera capture, YOLOv8n (nano model) for real-time object detection, and TTS (Text-to-Speech) to announce detected objects.

## Desktop Testing (Recommended First Step)

Before building for Android, it is highly recommended to run and test the app on your desktop. This ensures everything works and automatically downloads the YOLOv8n weights (`yolov8n.pt`).

### 1. Install Dependencies
Open a command prompt or terminal in this folder (`d:\EDP\object_detection_app`) and run:
```bash
pip install -r requirements.txt
```

### 2. Run the Application
Start the Kivy application by running:
```bash
python main.py
```
*Note: The first time you run this, `ultralytics` will download the `yolov8n.pt` weights file (about 6MB) into this directory. Make sure you are connected to the internet.*

## Building for Android (Buildozer)

Packaging a Python app with complex ML libraries like PyTorch/Ultralytics and OpenCV for Android requires a Linux environment. If you are on Windows, you will need to use Windows Subsystem for Linux (WSL).

### 1. Setup WSL (If on Windows)
1. Open PowerShell and run: `wsl --install -d Ubuntu`
2. Restart your computer and set up your Ubuntu username/password.
3. Open the "Ubuntu" app from your start menu.

### 2. Install Buildozer and Dependencies
Inside your Linux/WSL terminal, install the necessary packaging tools:
```bash
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
pip3 install buildozer cython virtualenv
```

### 3. Ensure `yolov8n.pt` is Present
Make sure you have already run the application on your desktop at least once so that `yolov8n.pt` is in the same directory as `main.py`. The `buildozer.spec` file is configured to include `.pt` files in the final APK.

### 4. Build the APK
Navigate to your project directory in WSL. For example, if your project is on `D:\EDP\object_detection_app`, you can access it in WSL via `/mnt/d/EDP/object_detection_app`:
```bash
cd /mnt/d/EDP/object_detection_app
buildozer android debug
```
*Warning: The first build will take a very long time (sometimes over an hour) as it downloads the Android NDK/SDK and cross-compiles Python, OpenCV, and PyTorch for ARM architecture.*

### 5. Deploy to Your Phone
Once the build completes successfully, the APK will be generated inside the `bin/` directory. You can transfer this to your Android phone or deploy it automatically if your phone is plugged in with USB Debugging enabled:
```bash
buildozer android debug deploy run
```

### Important Mobile Considerations
- **Performance:** Complex ML models are computationally heavy. The `yolov8n.pt` (nano) model is chosen for speed, but performance will depend heavily on your device's processor.
- **Troubleshooting:** Compiling ML libraries via Buildozer can sometimes run into native NDK compilation issues. If standard packaging fails, an alternative production route for Android is to export the YOLOv8 model to TFLite (`yolo export model=yolov8n.pt format=tflite`) and use `tflite-runtime` instead of `ultralytics` and `torch` in your requirements. The provided Kivy code uses standard `ultralytics` as requested.
