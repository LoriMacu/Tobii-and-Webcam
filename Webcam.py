#Code relative to the webcam

import cv2
import mediapipe as mp
import numpy as np
import time
import csv
import random
import sys
import matplotlib.pyplot as plt


# ========================
# USER DEFINED PARAMS
# ========================
SCREEN_WIDTH_CM = 25.0
VIEWING_DISTANCE_CM = 25.0


class Webcam():

    def __init__(self, cam_index=0, show_preview=True):
        """Initializes the webcam and MediaPipe."""
        self.cam_index = cam_index
        self.show_preview = show_preview
        self.cap = None
        self.frame_width = None
        self.frame_height = None
        #Mediapipe set-up
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.face_mesh = None # Initialize later
        
        self.drawing_spec = mp.solutions.drawing_utils.DrawingSpec(thickness=1, circle_radius=1)
        #self.drawing_styles = mp.solutions.drawing_styles
        self.gaze_data = {  
            'timestamps': [],
            'right_eye_x': [],
            'right_eye_y': [],
            'left_eye_x': [],
            'left_eye_y': [],
            'markers': []  # Changed from 'marker' to 'markers'
            }                    #(t,x,y)
        self._running = False
    
    def add_marker(self, marker_type):
        """
        Add a custom marker to the gaze data
        
        Args:
        - marker_type (str): Type of marker (e.g., 'STIMULUS_START', 'STIMULUS_END')
        """
        now = time.time()
        self.gaze_data['timestamps'].append(now)
        self.gaze_data['right_eye_x'].append(None)
        self.gaze_data['right_eye_y'].append(None)
        self.gaze_data['left_eye_x'].append(None)
        self.gaze_data['left_eye_y'].append(None)
        self.gaze_data['markers'].append(marker_type)
    
    
    def start_recording_webcam(self):
        """Starts the webcam and MediaPipe."""
        try:
            self.cap = cv2.VideoCapture(self.cam_index)
        
            if not self.cap.isOpened():
                print("Error: Could not open webcam.")
                return False
        
            self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                             max_num_faces=1,
                             min_detection_confidence=0.5,
                             min_tracking_confidence=0.5,
                             refine_landmarks=True)
            print("[Webcam] Starting capture... Press 'q' to quit.")
            self._running = True
            
            # Create window with a specific name and make it non-fullscreen
            cv2.namedWindow('MediaPipe FaceMesh', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('MediaPipe FaceMesh', 640, 480)  # Smaller window size
        
            # Process frames as long as _running is True
            while self._running:
                try:
                    ret, frame = self.cap.read()
                    if not ret:
                        print("Error: Could not read frame from webcam.")
                        time.sleep(0.1)  # Small delay before retrying
                        continue
                
                    # Process the frame
                    frame = cv2.flip(frame, 1)
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results = self.face_mesh.process(frame_rgb)
                
                    now = time.time()
                
                    if results.multi_face_landmarks:
                        for face_landmarks in results.multi_face_landmarks:
                            self.mp_drawing.draw_landmarks(
                                image=frame,
                                landmark_list=face_landmarks,
                                connections=self.mp_face_mesh.FACEMESH_TESSELATION,
                                landmark_drawing_spec=self.drawing_spec,
                                connection_drawing_spec=self.drawing_spec
                            )
            
                            # Extract eye position
                            rx = face_landmarks.landmark[473].x * self.frame_width
                            ry = face_landmarks.landmark[473].y * self.frame_height
                            lx = face_landmarks.landmark[468].x * self.frame_width
                            ly = face_landmarks.landmark[468].y * self.frame_height
            
                            self.gaze_data['timestamps'].append(now)
                            self.gaze_data['right_eye_x'].append(rx)
                            self.gaze_data['right_eye_y'].append(ry)
                            self.gaze_data['left_eye_x'].append(lx)
                            self.gaze_data['left_eye_y'].append(ly)
                            self.gaze_data['markers'].append(None)
                
                    if self.show_preview:
                        cv2.imshow('MediaPipe FaceMesh', frame)
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        break
                except Exception as e:
                    print(f"[Webcam] Error processing frame: {e}")
                    time.sleep(0.1)  # Small delay before continuing
        
            #Cleanup
            self._running = False
            if self.cap is not None and self.cap.isOpened():
                self.cap.release()
            cv2.destroyAllWindows()
            print("[Webcam] Capture stopped.")
        except Exception as e:
            print(f"[Webcam] Critical error in webcam recording: {e}")
            self._running = False
            if hasattr(self, 'cap') and self.cap is not None and self.cap.isOpened():
                self.cap.release()
            cv2.destroyAllWindows()
    
    def stop_recording(self):
        """Stops the capture loop from code (no 'q' key required)."""
        if self._running:
            print("[Webcam] Stopping capture...")
            self._running = False
            if self.cap is not None and self.cap.isOpened():
                self.cap.release()
            cv2.destroyAllWindows()
            print("[Webcam] Capture stopped.")
        

    def get_data(self):
        """Returns the gaze data."""
        return self.gaze_data

        


    def plot_eye_positions(self):
        """Plot eye positions from collected data."""
        data = self.get_data()
        
        plt.figure(figsize=(12, 6))
        
        plt.subplot(1, 2, 1)
        plt.plot(data['timestamps'], data['right_eye_x'], label='Right Eye X', color='red')
        plt.plot(data['timestamps'], data['right_eye_y'], label='Right Eye Y', color='green')
        plt.title('Right Eye Position vs Time')
        plt.xlabel('Time (s)')
        plt.ylabel('Position (pixels)')
        plt.legend()
        plt.grid(True)

        plt.subplot(1, 2, 2)
        plt.plot(data['timestamps'], data['left_eye_x'], label='Left Eye X', color='blue')
        plt.plot(data['timestamps'], data['left_eye_y'], label='Left Eye Y', color='orange')
        plt.title('Left Eye Position vs Time')
        plt.xlabel('Time (s)')
        plt.ylabel('Position (pixels)')
        plt.legend()
        plt.grid(True)

        plt.tight_layout()
        plt.show()


if __name__ == "__main__":

    webcam = Webcam()
    webcam.start_recording_webcam()
    #webcam.plot_eye_positions()
 


   
    





