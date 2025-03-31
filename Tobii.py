#Code relative to the tobii

import tobii_research as tr
import time
import sys
import os
import cv2
import numpy as np

class Tobii:

    #my_eyetracker = None
    #gaze_data =[]
    

    def __init__(self):

        self.my_eyetracker = None
        self.gaze_data = []
        self._recording = False
        self._subscription_handle = None
        
        
        found_eyetrackers = tr.find_all_eyetrackers()
        try:
           self.my_eyetracker = found_eyetrackers[0]
           print("Address: " + self.my_eyetracker.address)
           print("Model: " + self.my_eyetracker.model)
           print("Name (It's OK if this is empty): " + self.my_eyetracker.device_name)

        except IndexError:
        #my_eyetracker = None # No eyetracker found, set to None
           sys.exit("No eyetracker found")
        #print("No eyetracker found")
    
    def calibrate(self, calibration_points, screen_width, screen_height, point_radius, wait_time):

        if self.my_eyetracker is None: # Check if eyetracker is initialized before calibration
            print("[Tobii] No eyetracker available. Calibration cannot be started.")
            return

        calibration = tr.ScreenBasedCalibration(self.my_eyetracker)
        # Enter calibration mode.
        calibration.enter_calibration_mode()
        print(f"[Tobii] Entered calibration mode for eye tracker with serial number {self.my_eyetracker.serial_number}.") # Added serial number for clarity
        
        #Create an OpenCV window
        cv2.namedWindow("Calibration", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Calibration", screen_width, screen_height)
        #Start collecting data for the calibration points
        for i, (x,y) in enumerate(calibration_points, start=1):
            px = int(x * screen_width)
            py = int(y * screen_height)
            
            background = np.full((screen_height, screen_width, 3), 255, dtype=np.uint8)
            #Create the points in the screen
            # Draw the calibration circle
            cv2.circle(background, (px, py), point_radius, (0, 0, 255), -1)

            msg = f"Point {i}/{len(calibration_points)} at ({x:.2f}, {y:.2f})"
            cv2.putText(background, msg, (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,0,0), 2)
            cv2.imshow(window_name, background)
            cv2.waitKey(1)  # update the window

            # Wait for wait_time seconds so user can fixate
            start_time = time.time()
            while time.time() - start_time < wait_time:
                # If user presses 'q', you could break early (optional)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            # Collect data for this calibration point
            status = calibration.collect_data(x, y)
            print(f"Collect data at ({x:.2f}, {y:.2f}) => {status}")    
                        
            if status != tr.CALIBRATION_STATUS_SUCCESS:
                    # Try again if collection fails
                print(f"[Tobii] Collection failed for point {point}, trying again...")
                time.sleep(1) # Wait for the data to be collected
                status = calibration.collect_data(x, y)   
           
            
        
        # Attempt to compute calibration
        print("[Tobii] Computing and applying calibration.")
        calibration_result = calibration.compute_and_apply()
        print(f"[Tobii] compute_and_apply() returned: {calibration_result.status}")

        #Leave the calibration mode
        calibration.leave_calibration_mode()
        print("Left calibration mode.")
        cv2.destroyWindow(window_name)
        return calibration_result.status == tr.CALIBRATION_STATUS_SUCCESS


        
      
    def read_calibration(self):
        #Read the calibration
        filename = "saved_calibration.bin"
        
        with open(filename, "wb") as f:
            calibration_data = eyetracker.retrieve_calibration_data()
            if calibration_data is not None:
                f.write(calibration_data)
            else:
                print("No calibration data found.")
            
        print("Calibration data saved to", filename)

        with open(filename, "rb") as f:
            calibration_data = f.read()
            if len(calibration_data) > 0:
                eyetracker.apply_calibration_data(calibration_data)
                print("Calibration data loaded from", filename)
            else:
                print("No calibration data found in", filename)
                
        try:
            os.remove(filename)
        except OSError:
            print("No file found")
            pass
        
    def gaze_data_callback(self, gaze_data):

        gaze_data['system_timestamp'] = time.time()
        self.gaze_data.append(gaze_data)
        #left_gaze = gaze_data['left_gaze_point_on_display_area']
        #right_gaze = gaze_data['right_gaze_point_on_display_area']
    
    def add_marker(self, marker):

        """
        Add a custom marker to the gaze data
        
        Args:
        - marker_type (str): Type of marker (e.g., 'STIMULUS_START', 'STIMULUS_END')
        """
        marker_data = {
            'type': 'marker',
            'marker_type': marker,
            'system_timestamp': time.time()
        }
        self.gaze_data.append(marker_data)
    
    def start_recording(self):

        if self.my_eyetracker is None:
            print("[Tobii] No eyetracker found. Cannot start recording.")
            return
        if self._recording:
            print("[Tobii] is already recording.")
            return

        # Clear out old data if desired
        self.gaze_data.clear()

        self._subscription_handle = self.my_eyetracker.subscribe_to(
            tr.EYETRACKER_GAZE_DATA,
            self.gaze_data_callback,
            as_dictionary=True
        )
        self._recording = True
        self._subscription_handle = True
        print("[Tobii] Started recording (subscribed to gaze data).")

    def stop_recording(self):
                    
        if not self._recording:
            print("[Tobii] Not currently recording.")
            return
        if self.my_eyetracker is None or self._subscription_handle is None:
            print("[Tobii] No subscription handle to unsubscribe. Something's off.")
            return

        self.my_eyetracker.unsubscribe_from(
            tr.EYETRACKER_GAZE_DATA,
            self._subscription_handle
        )
        self._subscription_handle = None
        self._recording = False
        print("[Tobii] Stopped recording (unsubscribed).")

    
    def get_data(self):
        """Returns the collected gaze data."""
        return self.gaze_data







    

        

if __name__ == "__main__":

    pass
    
    #tobii.read_calibration()

      

        


   

    
