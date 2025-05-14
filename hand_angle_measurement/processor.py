import cv2
import numpy as np
import mediapipe as mp
import os

class ImageProcessor:
    """Handles image processing and angle calculations."""

    def __init__(self):
        """Initialize MediaPipe Hands model."""
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.4,
            min_tracking_confidence=0.4,
            model_complexity=1
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

    def calculate_angle_with_vertical(self, a, b):
        """Calculate the angle between two points relative to vertical."""
        a = np.array(a)
        b = np.array(b)
        vertical_vector = np.array([0, -1])
        hand_vector = b - a
        hand_vector = hand_vector / np.linalg.norm(hand_vector)

        dot_product = np.dot(hand_vector, vertical_vector)
        cross_product = np.cross(vertical_vector, hand_vector)

        angle_rad = np.arccos(np.clip(dot_product, -1.0, 1.0))
        angle_deg = np.degrees(angle_rad)

        if cross_product < 0:
            angle_deg = -angle_deg

        return angle_deg

    def preprocess_image(self, image):
        """Apply image preprocessing for better hand detection."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        equalized = clahe.apply(blurred)
        normalized = cv2.normalize(equalized, None, alpha=0, beta=255,
                                   norm_type=cv2.NORM_MINMAX)

        kernel = np.array([[0, -1, 0],
                           [-1, 5, -1],
                           [0, -1, 0]])
        sharpened = cv2.filter2D(normalized, -1, kernel)

        return cv2.cvtColor(sharpened, cv2.COLOR_GRAY2BGR)

    def process_image(self, image_path):
        """Process a single image and detect hand angles."""
        image_name = os.path.basename(image_path)
        image = cv2.imread(image_path)

        if image is None:
            return None, None, None

        # Resize large images
        if max(image.shape) > 1000:
            scale = 1000 / max(image.shape)
            image = cv2.resize(image, (0, 0), fx=scale, fy=scale)

        image = self.preprocess_image(image)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.hands.process(image_rgb)

        angles = []
        image_with_landmarks = np.copy(image_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    image_with_landmarks,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )

                # Get wrist and middle finger tip coordinates
                wrist = [
                    hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST].x * image.shape[1],
                    hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST].y * image.shape[0]
                ]
                middle_finger_tip = [
                    hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP].x * image.shape[1],
                    hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y * image.shape[0]
                ]

                angle = self.calculate_angle_with_vertical(wrist, middle_finger_tip)
                angles.append(angle)

                # Draw angle information
                cv2.putText(
                    image_with_landmarks,
                    f"{angle:.1f}°",
                    (int(wrist[0]), int(wrist[1]) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 0, 0),
                    2
                )

        return image_with_landmarks, angles, image_name