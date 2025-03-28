
import cv2
import numpy as np

class Stimulus:

    def __init__(self, screen_width, screen_height, screen_width_cm, screen_height_cm, cm_to_pixel):
        
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen_width_center = screen_width // 2
        self.screen_height_center = screen_height // 2
        
        #Convert cm to pixels

        self.offset_cm = [0, 5, -5, 10, -10]
        self.offset_pixel = [int(offset * cm_to_pixel) for offset in self.offset_cm]
       
        # Randomization parameters
        self.min_display_time = 2  # minimum display time in seconds
        self.max_display_time = 5  # maximum display time in seconds

        # Data recording
        self.stimulus_data = {
            'timestamps': [],
            'stimulus_positions': [],
            'stimulus_offsets_cm': []
        }

    
    def create_stimulus_screen(self, offset_pixel):

        """
        Create a screen with a stimulus point at the specified offset.
        
        Args:
        - offset_pixel (int): Horizontal offset from screen center in pixels
        
        Returns:
        - numpy array representing the stimulus screen

        """

        #Create a white screen

        screen = np.full((self.screen_height, self.screen_width, 3), 255, dtype=np.uint8)

        # Draw stimulus point (red circle)
        point_x = self.screen_center_x + offset_pixel
        point_y = self.screen_center_y
        cv2.circle(screen, (point_x, point_y), 20, (0, 0, 255), -1)
        
        return screen
    
    def stimulus_loop(self, num_sequence):
        """
        Loop through the stimulus points and display them on the screen.
        Start with a key press to start the loop.
        It returns the stimulus_data dictionary when the loop is done.

        """

        welcome_screen = np.full((self.screen_height, self.screen_width, 3), 255, dtype=np.uint8)
        welcome_text = "Press c to start the stimulus presentation"
        cv2.putText(welcome_screen, 
                    welcome_text, 
                    (self.screen_width//4, self.screen_height//2),  #Position of the text
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    1.5, (0, 0, 0), 3)
        
        cv2.imshow('Stimulus Presentation', welcome_screen)

        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == ord('c'):
                break

        cv2.destroyAllWindows()

        #Stimulus presentation loop

        cv2.namedWindow('Stimulus Presentation', cv2.WINDOW_NORMAL)
        cv2.setWindowProperty('Stimulus Presentation', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        for _ in range(num_sequence):
            for offset_cm, offset_pixel in zip(self.offset_cm, self.offset_pixel): #zip() allows us to iterate over two lists simultaneously:

                stimulus_screen = self.create_stimulus_screen(offset_pixel)
                cv2.imshow('Stimulus Presentation', stimulus_screen)

                #Random_display_time
                display_time = np.random.uniform(self.min_display_time, self.max_display_time)
                
                # Record stimulus presentation data
                start_time = time.time()
                self.stimulus_data['timestamps'].append(start_time)
                self.stimulus_data['stimulus_positions'].append(offset_pixel)
                self.stimulus_data['stimulus_offsets_cm'].append(offset_cm)
                
                # Wait for specified time or key press
                start_wait = time.time()
                while time.time() - start_wait < display_time:
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        cv2.destroyAllWindows()
                        return self.stimulus_data
                
                # Blank screen between stimuli
                blank_screen = np.full((self.screen_height, self.screen_width, 3), 255, dtype=np.uint8)
                cv2.imshow('Stimulus Presentation', blank_screen)
                cv2.waitKey(1000)  # 1-second break between stimuli
        
        cv2.destroyAllWindows()
        return self.stimulus_data
                
        

        


