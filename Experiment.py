from Tobii import Tobii 
from Webcam import Webcam
import time
import cv2
import numpy as np
import threading
from Stimulus import Stimulus
import csv
import datetime

def save_data(stimulus_data, tobii_data, webcam_data):

        """
        Save experimental data to CSV files.
        
        Args:
            stimulus_data (dict): Stimulus presentation data
            tobii_data (list): Tobii eye tracking data
            webcam_data (dict): Webcam eye tracking data
        """
    
        timestamp_now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save stimulus data
        with open(f'stimulus_data_{timestamp_now}.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Stimulus Position (px)', 'Stimulus Offset (cm)'])
            for i in range(len(stimulus_data['timestamps'])):
                writer.writerow([
                    stimulus_data['timestamps'][i],
                    stimulus_data['stimulus_positions'][i],
                    stimulus_data['stimulus_offsets_cm'][i]
                ])

        with open(f'tobii_data_{timestamp_now}.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            if tobii_data:
                writer.writerow(['System Timestamp']+list(tobii_data[0].keys()))
                for data_point in tobii_data:
                    row = [data_point.get('system_timestamp', '')] + [data_point.get(key, '') for key in tobii_data[0].keys()]
                    writer.writerow(row)


        with open(f'webcam_gaze_data_{timestamp_now}.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Right Eye X', 'Right Eye Y', 'Left Eye X', 'Left Eye Y', 'Markers'])
            for i in range(len(webcam_data['timestamps'])):
                writer.writerow([
                    webcam_data['timestamps'][i],
                    webcam_data['right_eye_x'][i],
                    webcam_data['right_eye_y'][i],
                    webcam_data['left_eye_x'][i],
                    webcam_data['left_eye_y'][i],
                    webcam_data['markers'][i]
                ])

        print(f"[Experiment] Data saved with timestamp: {timestamp_now}")

def main():
    screen_width = 1920
    screen_height = 1200
    screen_width_cm = 38
    screen_height_cm = 24
    point_radius = 5
    wait_time = 5
    num_sequence = 3
    cm_to_pixel = screen_width / screen_width_cm

    tobii_tracker = None
    webcam = None
    webcam_thread = None

    try:
        # Initialize Tobii
        tobii_tracker = Tobii()
        #Initialize Webcam
        webcam = Webcam(show_preview=False)  # Set to False to reduce window conflicts

        # Prepare for data collection
        input("[Experiment] Press Enter to start the experiment...")
        
        #Start recording - use threading for webcam to avoid blocking
        tobii_tracker.start_recording()
        webcam_thread = threading.Thread(target=webcam.start_recording_webcam)
        webcam_thread.daemon = True  # This allows the thread to exit when the main program exits
        webcam_thread.start()

        # Add flags
        tobii_tracker.add_marker('Start stimulus')
        webcam.add_marker('Start stimulus')

        # Give webcam time to initialize
        time.sleep(2)  # Increased delay for better initialization

        #initialize Stimulus
        stimulus = Stimulus(screen_width, screen_height, screen_width_cm, screen_height_cm, cm_to_pixel)
        
        print("[Experiment] Starting stimulus presentation...")
        
        # Don't create window here - let the Stimulus class handle its own windows
        # Remove these lines:
        # cv2.namedWindow('Stimulus Presentation', cv2.WINDOW_NORMAL)
        # cv2.setWindowProperty('Stimulus Presentation', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        # cv2.setWindowProperty('Stimulus Presentation', cv2.WND_PROP_TOPMOST, 1)
        
        # Brief delay to ensure window focus
        time.sleep(0.5)
        
        stimulus_data = stimulus.stimulus_loop(num_sequence)

        # Add marker for end of stimulus
        tobii_tracker.add_marker('End stimulus')
        webcam.add_marker('End stimulus')

        #Stop recording
        print("[Experiment] Stopping recordings...")
        tobii_tracker.stop_recording()
        webcam.stop_recording()
        if webcam_thread:
            webcam_thread.join(timeout=3)  # Wait for webcam thread to finish, but not forever

        # Retrieve data
        print("[Experiment] Retrieving data...")
        tobii_gaze_data = tobii_tracker.get_data()
        webcam_gaze_data = webcam.get_data()
        save_data(stimulus_data, tobii_gaze_data, webcam_gaze_data)
        print("[Experiment] Experiment completed successfully!")

    except Exception as e:
        print(f"[Experiment] An error occurred: {e}")
        import traceback
        traceback.print_exc()  # Print the full error traceback for debugging
    finally:
        # Ensure cleanup happens even if there's an error
        print("[Experiment] Cleaning up resources...")
        if tobii_tracker:
            try:
                tobii_tracker.stop_recording()
            except:
                pass
        if webcam:
            try:
                webcam.stop_recording()
            except:
                pass
        # Force destroy all OpenCV windows
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()



        







 



    
    
