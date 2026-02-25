import cv2
import numpy as np
import threading
import time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.utils import platform
from ultralytics import YOLO

# TTS Handling
try:
    if platform == 'android':
        from plyer import tts
    else:
        import pyttsx3
        # Ensure engine is instantiated correctly outside threads
        engine = pyttsx3.init()
except Exception as e:
    print(f"TTS Initialization Error: {e}")

class ObjectDetectorApp(App):
    def build(self):
        # Load YOLOv8n (nano version for low-resource devices)
        self.model = YOLO('yolov8n.pt')
        
        self.capture = None
        self.is_detecting = False
        
        # Concurrency and UI state
        self.frame = None
        self.processed_frame = None
        self.running_inference = False
        self.lock = threading.Lock()
        
        # Cooldown management for voice alerts
        self.last_announced = {}
        self.announce_cooldown = 5.0  # seconds between announcing the same object type
        self.speech_lock = threading.Lock() # Prevents overlapping speech on desktop
        
        # UI Setup
        layout = BoxLayout(orientation='vertical')
        
        # Camera preview
        self.image = Image(size_hint=(1, 0.8))
        layout.add_widget(self.image)
        
        # Start/Stop Button
        self.btn = Button(text="Start Detection", size_hint=(1, 0.2), font_size='24sp', 
                          background_color=(0, 0.5, 1, 1))
        self.btn.bind(on_press=self.toggle_detection)
        layout.add_widget(self.btn)
        
        return layout

    def on_start(self):
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.CAMERA, Permission.RECORD_AUDIO, Permission.INTERNET, Permission.VIBRATE])

    def toggle_detection(self, instance):
        if not self.is_detecting:
            self.start_camera()
        else:
            self.stop_camera()

    def start_camera(self):
        # Index 0 is typically the default camera. On mobile it might be back camera.
        self.capture = cv2.VideoCapture(0)
        
        # Lower resolution for FPS improvement on mobile
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        self.is_detecting = True
        self.btn.text = "Stop Detection"
        self.btn.background_color = (1, 0, 0, 1) # Red means stop
        
        # Update UI up to 30 times a second to keep camera feed smooth
        Clock.schedule_interval(self.update_ui, 1.0/30.0)

    def stop_camera(self):
        self.is_detecting = False
        self.btn.text = "Start Detection"
        self.btn.background_color = (0, 0.5, 1, 1)
        Clock.unschedule(self.update_ui)
        
        if self.capture:
            self.capture.release()
            self.capture = None
        
        # Clear the display
        self.image.texture = None

    def update_ui(self, dt):
        """ Runs in Kivy main thread. Grabs latest frame and displays it. Spawns ML thread. """
        if not self.capture:
            return

        ret, frame = self.capture.read()
        if not ret:
            return
            
        # Store latest frame for inference thread
        with self.lock:
            self.frame = frame.copy()
            
        # If inferencer is ready for a new frame, launch a background thread
        if not self.running_inference:
            self.running_inference = True
            threading.Thread(target=self.run_inference, daemon=True).start()

        # Display whichever frame was last processed (or raw if none yet)
        display_frame = self.processed_frame if self.processed_frame is not None else frame
        
        # Convert OpenCV BGR to RGB sequence for Kivy
        buf1 = cv2.flip(display_frame, 0) # Flip vertically since Kivy draws from bottom up
        buf = buf1.tobytes()
        texture = Texture.create(size=(display_frame.shape[1], display_frame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.image.texture = texture

    def run_inference(self):
        """ Runs in a background thread to prevent UI freezing """
        with self.lock:
            if self.frame is None:
                self.running_inference = False
                return
            infer_frame = self.frame.copy()

        # Perform YOLO inference. Verbose=False to save console spam
        results = self.model(infer_frame, verbose=False)
        detected_objects = set()
        
        # Draw bounding boxes and collect object names
        for r in results:
            boxes = r.boxes
            for box in boxes:
                conf = float(box.conf[0])
                if conf > 0.5: # 50% confidence threshold
                    cls_id = int(box.cls[0])
                    class_name = self.model.names[cls_id]
                    detected_objects.add(class_name)
                    
                    # Draw Bounding Box
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cv2.rectangle(infer_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(infer_frame, f"{class_name}", (x1, max(10, y1 - 10)), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Trigger speech for detected objects (Spawns its own thread internally)
        self.handle_speech(list(detected_objects))

        # Pass processed frame back to UI thread so it can be displayed
        self.processed_frame = infer_frame
        self.running_inference = False


    def handle_speech(self, objects):
        """ Checks cooldowns and fires speech """
        current_time = time.time()
        for obj in objects:
            if obj not in self.last_announced or (current_time - self.last_announced[obj]) > self.announce_cooldown:
                self.last_announced[obj] = current_time
                self.speak_async(obj)

    def speak_async(self, text):
        def _speak():
            if platform == 'android':
                try:
                    tts.speak(message=text)
                except Exception as e:
                    print(f"Android TTS Error: {e}")
            else:
                # Desktop TTS (pyttsx3) crashes if multithreaded without locks/engine recreation
                with self.speech_lock:
                    try:
                        import pythoncom
                        pythoncom.CoInitialize() # Required for Windows threading TTS
                        engine = pyttsx3.init()
                        engine.say(text)
                        engine.runAndWait()
                    except Exception as e:
                        print(f"Desktop TTS Error: {e}")

        # Start speech thread
        threading.Thread(target=_speak, daemon=True).start()

    def on_stop(self):
        self.stop_camera()

if __name__ == '__main__':
    ObjectDetectorApp().run()
