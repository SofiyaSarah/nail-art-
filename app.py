import streamlit as st
import cv2
import numpy as np
import mediapipe as mp
from PIL import Image
import colorsys

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Enhanced color suggestions with more options
COLOR_SUGGESTIONS = {
    "very_light": {
        "primary": ["Soft Pink 🌸", "Pearl White 🤍", "Light Rose 🌹"],
        "bold": ["Classic Red ❤️", "Deep Purple 💜", "Navy Blue 💙"],
        "trendy": ["Mint Green 💚", "Lavender 💜", "Peach 🍑"]
    },
    "light": {
        "primary": ["Rose Pink 🌹", "Coral 🪸", "Light Berry 🫐"],
        "bold": ["Cherry Red 🍒", "Royal Blue 👑", "Emerald Green 💎"],
        "trendy": ["Sage Green 🌿", "Dusty Rose 🥀", "Champagne 🥂"]
    },
    "medium": {
        "primary": ["Warm Coral ❤️", "Mauve 💜", "Terracotta 🏺"],
        "bold": ["Crimson Red ❤️‍🔥", "Sapphire Blue 💙", "Forest Green 🌲"],
        "trendy": ["Burnt Orange 🔥", "Plum 🟣", "Bronze ✨"]
    },
    "dark": {
        "primary": ["Gold Glitter ✨", "Rich Burgundy 🍷", "Deep Plum 🟣"],
        "bold": ["Bright Red 🔴", "Electric Blue ⚡", "Jade Green 💚"],
        "trendy": ["Copper 🔶", "Midnight Blue 🌙", "Rose Gold 🌹✨"]
    },
    "very_dark": {
        "primary": ["Rose Gold 🌹✨", "Deep Wine 🍷", "Rich Brown 🤎"],
        "bold": ["Fire Red 🔥", "Cobalt Blue 🔷", "Emerald 💎"],
        "trendy": ["Metallic Silver 🪙", "Deep Teal 🌊", "Golden Bronze 🏆"]
    }
}

def get_enhanced_skin_tone(bgr_color):
    """Enhanced skin tone detection using multiple color spaces"""
    # Convert to different color spaces for better analysis
    rgb_color = cv2.cvtColor(np.uint8([[bgr_color]]), cv2.COLOR_BGR2RGB)[0][0]
    hsv_color = cv2.cvtColor(np.uint8([[bgr_color]]), cv2.COLOR_BGR2HSV)[0][0]
    lab_color = cv2.cvtColor(np.uint8([[bgr_color]]), cv2.COLOR_BGR2LAB)[0][0]
    
    r, g, b = rgb_color
    h, s, v = hsv_color
    l, a, b_lab = lab_color
    
    # Individual Typology Angle (ITA) calculation for more accurate skin tone
    ita = np.arctan2(b_lab - 50, l - 50) * 180 / np.pi
    
    # Classify based on ITA and brightness
    brightness = v
    
    if ita > 55 or brightness > 220:
        return "very_light"
    elif ita > 41 or (brightness > 180 and s < 60):
        return "light"
    elif ita > 28 or (brightness > 120 and brightness <= 180):
        return "medium"
    elif ita > 10 or (brightness > 80 and brightness <= 120):
        return "dark"
    else:
        return "very_dark"

def process_hand_landmarks(image, hands_model):
    """Process image to detect hand landmarks"""
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands_model.process(rgb_image)
    return results

def extract_skin_color(image, hand_landmarks, image_shape):
    """Extract skin color from multiple points for better accuracy"""
    h, w = image_shape[:2]
    
    # Sample multiple landmarks for better skin tone detection
    sample_points = [9, 13, 17, 5, 1]  # Various finger bases and wrist
    colors = []
    
    for point_idx in sample_points:
        if point_idx < len(hand_landmarks.landmark):
            landmark = hand_landmarks.landmark[point_idx]
            cx, cy = int(landmark.x * w), int(landmark.y * h)
            
            if 0 <= cx < w and 0 <= cy < h:
                # Sample a small area around the point for better color averaging
                sample_area = image[max(0, cy-2):min(h, cy+3), max(0, cx-2):min(w, cx+3)]
                if sample_area.size > 0:
                    avg_color = np.mean(sample_area.reshape(-1, 3), axis=0)
                    colors.append(avg_color)
    
    if colors:
        # Return average color from all sample points
        return np.mean(colors, axis=0).astype(int)
    return None

def main():
    st.set_page_config(
        page_title="AI Nail Polish Advisor",
        page_icon="💅",
        layout="wide"
    )
    
    st.title("💅 AI Nail Polish Color Advisor")
    st.markdown("*Discover your perfect nail polish colors based on your skin tone!*")
    
    # Sidebar configuration
    st.sidebar.header("Settings")
    detection_confidence = st.sidebar.slider("Detection Confidence", 0.1, 1.0, 0.7, 0.1)
    tracking_confidence = st.sidebar.slider("Tracking Confidence", 0.1, 1.0, 0.7, 0.1)
    
    # Color category selection
    color_category = st.sidebar.selectbox(
        "Color Category",
        ["primary", "bold", "trendy"],
        help="Choose the type of colors you prefer"
    )
    
    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📸 Camera Feed")
        
        # Camera input
        camera_input = st.camera_input("Take a picture of your hand")
        
        if camera_input is not None:
            # Convert the image
            image = Image.open(camera_input)
            image_array = np.array(image)
            
            # Process with MediaPipe
            with mp_hands.Hands(
                static_image_mode=True,
                max_num_hands=2,
                min_detection_confidence=detection_confidence,
                min_tracking_confidence=tracking_confidence
            ) as hands:
                
                results = process_hand_landmarks(image_array, hands)
                
                if results.multi_hand_landmarks:
                    # Draw landmarks on image
                    annotated_image = image_array.copy()
                    
                    skin_tones_detected = []
                    
                    for hand_landmarks in results.multi_hand_landmarks:
                        # Draw hand landmarks
                        mp_drawing.draw_landmarks(
                            annotated_image, 
                            hand_landmarks, 
                            mp_hands.HAND_CONNECTIONS,
                            mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2),
                            mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
                        )
                        
                        # Extract and analyze skin color
                        skin_color = extract_skin_color(
                            image_array, 
                            hand_landmarks, 
                            image_array.shape
                        )
                        
                        if skin_color is not None:
                            skin_tone = get_enhanced_skin_tone(skin_color)
                            skin_tones_detected.append(skin_tone)
                    
                    # Display annotated image
                    st.image(annotated_image, caption="Hand Detection Results", use_column_width=True)
                    
                    # Show results
                    if skin_tones_detected:
                        most_common_tone = max(set(skin_tones_detected), key=skin_tones_detected.count)
                        
                        with col2:
                            st.header("🎨 Your Recommendations")
                            
                            st.success(f"**Detected Skin Tone:** {most_common_tone.replace('_', ' ').title()}")
                            
                            suggestions = COLOR_SUGGESTIONS[most_common_tone][color_category]
                            
                            st.subheader(f"Perfect {color_category.title()} Colors:")
                            
                            for i, color in enumerate(suggestions, 1):
                                st.markdown(f"**{i}.** {color}")
                            
                            # Additional tips
                            st.subheader("💡 Pro Tips")
                            
                            tips = {
                                "very_light": "Consider nude tones for everyday, bright colors for special occasions",
                                "light": "Soft pastels and classic reds complement your tone beautifully",
                                "medium": "You can pull off both warm and cool tones - experiment freely!",
                                "dark": "Rich, deep colors and metallics will make your hands pop",
                                "very_dark": "Bold, vibrant colors and metallics are stunning on you"
                            }
                            
                            st.info(tips.get(most_common_tone, "Experiment with different shades to find your favorites!"))
                            
                            # Show all categories
                            with st.expander("See all color categories"):
                                for category, colors in COLOR_SUGGESTIONS[most_common_tone].items():
                                    st.write(f"**{category.title()}:** {', '.join(colors)}")
                    
                else:
                    st.warning("No hands detected in the image. Please ensure your hand is clearly visible and try again.")
        
        else:
            st.info("👆 Take a photo of your hand using the camera above to get personalized nail polish recommendations!")
    
    # Instructions
    with st.expander("📋 How to use this app"):
        st.markdown("""
        1. **Take a clear photo** of your hand using the camera input above
        2. **Ensure good lighting** - natural light works best
        3. **Keep your hand steady** and fill most of the frame
        4. **Wait for detection** - the app will automatically detect your hand and skin tone
        5. **Get your recommendations** - personalized nail polish colors will appear on the right
        
        **Tips for best results:**
        - Use natural lighting when possible
        - Keep your hand flat and fingers spread slightly
        - Avoid shadows or harsh lighting
        - Make sure your hand takes up most of the photo
        """)
    
    # Technical info
    with st.expander("🔧 Technical Details"):
        st.markdown("""
        This app uses:
        - **MediaPipe** for hand landmark detection
        - **Computer Vision** for skin tone analysis
        - **Individual Typology Angle (ITA)** calculation for accurate skin tone classification
        - **Multiple color space analysis** (RGB, HSV, LAB) for robust color detection
        """)

if __name__ == "__main__":
    main()