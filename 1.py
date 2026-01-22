import cv2
import numpy as np
from ultralytics import YOLO
import time
import math

class EngagementTracker:
    def __init__(self):
        # Load YOLOv8 Pose model (optimized for speed)
        print("Loading YOLOv8 AI Model. Please wait...")
        self.model = YOLO('yolov8n-pose.pt')
        
        # Engagement Metrics
        self.attention_score = 100
        self.engagement_status = "Scanning..."
        self.focus_timer = 0
        self.last_engaged_time = time.time()
        
        # Colors (Neo-Cyberpunk Palette)
        self.colors = {
            'cyan': (255, 255, 0),    # Cyan (BGR)
            'magenta': (255, 0, 255),
            'green': (0, 255, 0),
            'red': (0, 0, 255),
            'dark': (20, 20, 20)
        }

    def draw_hud(self, frame, keypoints):
        h, w = frame.shape[:2]
        overlay = frame.copy()
        
        # Darken background slightly for contrast
        # cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 0), -1)
        # cv2.addWeighted(overlay, 0.1, frame, 0.9, 0, frame)

        # 1. Draw Tech Borders
        cv2.line(frame, (20, 20), (100, 20), self.colors['cyan'], 2)
        cv2.line(frame, (20, 20), (20, 100), self.colors['cyan'], 2)
        cv2.line(frame, (w-20, 20), (w-100, 20), self.colors['cyan'], 2)
        cv2.line(frame, (w-20, 20), (w-20, 100), self.colors['cyan'], 2)
        
        cv2.line(frame, (20, h-20), (100, h-20), self.colors['cyan'], 2)
        cv2.line(frame, (20, h-20), (20, h-100), self.colors['cyan'], 2)
        cv2.line(frame, (w-20, h-20), (w-100, h-20), self.colors['cyan'], 2)
        cv2.line(frame, (w-20, h-20), (w-20, h-100), self.colors['cyan'], 2)

        # 2. Keypoints Visualization (Face mesh type look)
        if len(keypoints) > 0:
            # Nose, Eyes, Ears (Indices 0-4)
            face_indices = [0, 1, 2, 3, 4]
            kp = keypoints[0].cpu().numpy() # Get first person
            
            # Connect eyes to nose
            if kp[0][2] > 0.5 and kp[1][2] > 0.5 and kp[2][2] > 0.5: # Confidence check
                nose = (int(kp[0][0]), int(kp[0][1]))
                left_eye = (int(kp[1][0]), int(kp[1][1]))
                right_eye = (int(kp[2][0]), int(kp[2][1]))
                
                # Draw triangular gaze connect
                cv2.line(frame, nose, left_eye, self.colors['magenta'], 1)
                cv2.line(frame, nose, right_eye, self.colors['magenta'], 1)
                cv2.line(frame, left_eye, right_eye, self.colors['magenta'], 1)
                
                # Draw Keypoints
                for i in face_indices:
                    if kp[i][2] > 0.5:
                        x, y = int(kp[i][0]), int(kp[i][1])
                        cv2.circle(frame, (x, y), 3, self.colors['cyan'], -1)

    def calculate_engagement(self, keypoints):
        if len(keypoints) == 0:
            return 0, "No Subject"

        kp = keypoints[0].cpu().numpy()
        
        # Check required facial points confidence (Nose, L-Eye, R-Eye)
        if kp[0][2] < 0.5 or kp[1][2] < 0.5 or kp[2][2] < 0.5:
            return 20, "Low Visibility"

        nose_x = kp[0][0]
        left_eye_x = kp[1][0]
        right_eye_x = kp[2][0]

        # Calculate horizontal gaze direction
        # Distances from nose to eyes can indicate head yaw
        eye_midpoint = (left_eye_x + right_eye_x) / 2
        deviation = abs(nose_x - eye_midpoint)
        eye_width = abs(right_eye_x - left_eye_x)
        
        # Normalize deviation
        if eye_width > 0:
            yaw_ratio = deviation / eye_width
        else:
            yaw_ratio = 1.0

        # Heuristic: If nose is centered (ratio ~0), looking front. 
        # If ratio > 0.5, likely looking side.
        
        raw_score = max(0, 100 - (yaw_ratio * 200)) # Penalize yaw
        
        # Smooth the score
        self.attention_score = (self.attention_score * 0.8) + (raw_score * 0.2)
        
        if self.attention_score > 60:
            return self.attention_score, "ENGAGED"
        elif self.attention_score > 30:
            return self.attention_score, "DISTRACTED"
        else:
            return self.attention_score, "LOOKING AWAY"

    def run(self):
        cap = cv2.VideoCapture(0)
        cap.set(3, 1280)
        cap.set(4, 720)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Flip for mirror effect
            frame = cv2.flip(frame, 1)
            h, w = frame.shape[:2]

            # AI Inference
            results = self.model(frame, verbose=False, stream=True)
            
            # Process results
            person_found = False
            for result in results:
                if result.keypoints is not None and len(result.keypoints.data) > 0:
                    kp = result.keypoints.data
                    
                    self.draw_hud(frame, kp)
                    score, status = self.calculate_engagement(kp)
                    self.engagement_status = status
                    self.attention_score = score
                    person_found = True
                    break # Track first person only
            
            if not person_found:
                self.engagement_status = "SEARCHING..."
                self.attention_score = max(0, self.attention_score - 5)

            # --- UI RENDERING ---
            # 1. Progress Bar for Engagement
            bar_width = 300
            bar_height = 20
            bar_x = 50
            bar_y = h - 50
            
            fill_width = int((self.attention_score / 100) * bar_width)
            
            # Color based on score
            if self.attention_score > 70: color = self.colors['green']
            elif self.attention_score > 40: color = self.colors['cyan']
            else: color = self.colors['red']

            # Draw Bar
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (50, 50, 50), -1)
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_width, bar_y + bar_height), color, -1)
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (255, 255, 255), 1)
            
            cv2.putText(frame, f"ATTENTION: {int(self.attention_score)}%", (bar_x, bar_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # 2. Status Text
            cv2.putText(frame, f"STATUS: {self.engagement_status}", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
            
            # 3. FPS/System Info
            cv2.putText(frame, "AI-VISION-SYS v1.0", (w - 200, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)

            cv2.imshow("Real-Time Engagement Tracker - YOLOv8", frame)

            if cv2.waitKey(1) & 0xFf == 27: # ESC
                break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = EngagementTracker()
    app.run()
