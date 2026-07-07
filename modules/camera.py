"""
SEVAGOTH Camera & Vision Module
Handles camera feed, face detection, and environment analysis
"""

import cv2
import time
from config import (
    CAMERA_INDEX, CAMERA_FRAME_RATE,
    CAMERA_BRIGHTNESS_LOW_THRESHOLD, CAMERA_BRIGHTNESS_HIGH_THRESHOLD,
    FACE_CASCADE_PATH, FACE_DETECTION_SCALE, FACE_DETECTION_MIN_NEIGHBORS
)


def camera_eye():
    """
    Display continuous camera feed from webcam
    Press 'q' to close the window
    Camera system remains active
    """
    try:
        cap = cv2.VideoCapture(CAMERA_INDEX)
        if not cap.isOpened():
            print("[SEVAGOTH VISION] Camera initialization failed - camera not available")
            return
        
        print("[SEVAGOTH VISION] Camera activated - visual sensors online")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[SEVAGOTH VISION] Frame capture failed - reconnecting...")
                time.sleep(1)
                continue
            
            cv2.imshow("SEVAGOTH's Vision", frame)
            
            # Press 'q' to close display window
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("[SEVAGOTH VISION] Closing visual display (camera remains active)")
                break
        
        cap.release()
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"[SEVAGOTH VISION ERROR] {e}")


def detect_faces():
    """
    Detect faces and analyze environment in real-time
    Shows lighting conditions, face count, and detail density
    Press 'q' to close the window
    """
    try:
        cap = cv2.VideoCapture(CAMERA_INDEX)
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + FACE_CASCADE_PATH
        )
        
        if not cap.isOpened():
            print("[SEVAGOTH FACE DETECTOR] Camera not available")
            return
        
        print("[SEVAGOTH FACE DETECTOR] Facial recognition system activated")
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[SEVAGOTH FACE DETECTOR] Frame capture failed - reconnecting...")
                time.sleep(1)
                continue
            
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=FACE_DETECTION_SCALE,
                minNeighbors=FACE_DETECTION_MIN_NEIGHBORS
            )
            
            # Draw rectangles around faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, "FACE DETECTED", (x, y - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Analyze environment every 30 frames
            frame_count += 1
            if frame_count % 30 == 0:
                brightness = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).mean()
                
                # Detect edges for environment details
                edges = cv2.Canny(gray, 50, 150)
                edge_density = cv2.countNonZero(edges) / (frame.shape[0] * frame.shape[1])
                
                # Classify lighting
                if brightness < CAMERA_BRIGHTNESS_LOW_THRESHOLD:
                    env_status = "LOW LIGHT"
                    color = (0, 0, 255)  # Red
                elif brightness > CAMERA_BRIGHTNESS_HIGH_THRESHOLD:
                    env_status = "BRIGHT"
                    color = (0, 255, 255)  # Yellow
                else:
                    env_status = "OPTIMAL"
                    color = (0, 255, 0)  # Green
                
                # Display environment info on frame
                cv2.putText(frame, f"Environment: {env_status}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                cv2.putText(frame, f"Faces: {len(faces)} | Details: {int(edge_density*100)}%",
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            cv2.imshow("SEVAGOTH Facial & Environmental Analysis", frame)
            
            # Press 'q' to close detection display
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("[SEVAGOTH FACE DETECTOR] Closing detection display (system remains active)")
                break
        
        cap.release()
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"[SEVAGOTH FACE DETECTOR ERROR] {e}")


def check_environment(cap):
    """
    Analyze current environment lighting and conditions
    
    Args:
        cap: OpenCV VideoCapture object
    """
    try:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture environment frame.")
            return
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        brightness = gray.mean()
        contrast = gray.std()
        
        # Classify lighting conditions
        if brightness < CAMERA_BRIGHTNESS_LOW_THRESHOLD:
            print("🌙 Environment: Dim lighting detected.")
        elif brightness > CAMERA_BRIGHTNESS_HIGH_THRESHOLD:
            print("☀️ Environment: Bright lighting detected.")
        else:
            print("💡 Environment: Moderate lighting.")
        
        print(f"   Brightness Level: {brightness:.2f} | Contrast: {contrast:.2f}")
    except Exception as e:
        print(f"[SEVAGOTH ENVIRONMENT ERROR] {e}")


def get_frame_from_camera():
    """
    Capture a single frame from camera
    
    Returns:
        tuple: (success, frame) where frame is the captured image
    """
    try:
        cap = cv2.VideoCapture(CAMERA_INDEX)
        ret, frame = cap.read()
        cap.release()
        return ret, frame
    except Exception as e:
        print(f"[SEVAGOTH CAMERA ERROR] {e}")
        return False, None