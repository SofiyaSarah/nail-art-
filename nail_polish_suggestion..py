import cv2
import numpy as np
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Simple skin tone → nail polish suggestions
color_suggestions = {
    "light": "Soft Pink 🌸",
    "medium": "Coral Red ❤️",
    "dark": "Gold Glitter ✨"
}

def get_skin_tone_color(bgr_color):
    hsv = cv2.cvtColor(np.uint8([[bgr_color]]), cv2.COLOR_BGR2HSV)[0][0]
    h, s, v = hsv
    if v > 200:
        return "light"
    elif 120 < v <= 200:
        return "medium"
    else:
        return "dark"

cap = cv2.VideoCapture(0)

with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7) as hands:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                h, w, c = frame.shape
                landmark = hand_landmarks.landmark[9]  # middle finger base
                cx, cy = int(landmark.x * w), int(landmark.y * h)

                if 0 <= cx < w and 0 <= cy < h:
                    bgr_color = frame[cy, cx]
                    skin_tone = get_skin_tone_color(bgr_color)
                    suggestion = color_suggestions[skin_tone]

                    cv2.putText(frame, f"Suggested Color: {suggestion}",
                                (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (255, 0, 255), 2)
                    cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

        cv2.imshow("Nail Polish Suggestion", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
