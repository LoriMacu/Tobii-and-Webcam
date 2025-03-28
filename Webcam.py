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
            'left_eye_y': []
            }                    #(t, x,y)
        self._running = False
    
    def start_recording_webcam(self):
        """Starts the webcam and MediaPipe."""
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

        while self._running:
            ret, frame = self.cap.read()
            if not ret:
                print("Error: Could not read frame from webcam.")
                break

            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(frame_rgb)

            now = time.time()

            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=drawing_spec,
                    connection_drawing_spec=drawing_spec
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

            cv2.imshow('MediaPipe FaceMesh', frame)
            if cv2.waitKey(0) & 0xFF == ord('q'):
                break

        #Cleanup
        self._running = False
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
    





