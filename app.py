import streamlit as st
import cv2
import numpy as np
from PIL import Image
import requests
from io import BytesIO
import base64


# Install required packages if not available
try:
    import mediapipe as mp
except ImportError:
    st.error("Please install mediapipe: pip install mediapipe")
    st.stop()

# Comprehensive color palette with skin tone specific recommendations
COMPREHENSIVE_COLOR_PALETTE = {
    "very_light_specific": {
        "display_name": "🌸 Perfect for Very Light Skin",
        "colors": [
            {"name": "Soft Rose Quartz", "hex": "#F7E7E7", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-50-pearl-pink", "price": "₹149"},
            {"name": "Delicate Lavender", "hex": "#E6E6FA", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-lavender-love", "price": "₹149"},
            {"name": "Cool Nude Pink", "hex": "#F5E6E8", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer", "price": "₹149"},
            {"name": "Ice Blue", "hex": "#E0F6FF", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-sky-high", "price": "₹149"},
            {"name": "Barely There Shimmer", "hex": "#F8F8FF", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-glitter-01-rose-quartz", "price": "₹199"},
        ]
    },
    "light_specific": {
        "display_name": "🌺 Perfect for Light Skin",
        "colors": [
            {"name": "Peachy Keen", "hex": "#FFDBAC", "link": "https://www.sugarcosmetics.com/products/tip-tac-toe-nail-lacquer-peach-please", "price": "₹299"},
            {"name": "Coral Blush", "hex": "#FF7F7F", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-coral-vibes", "price": "₹149"},
            {"name": "Soft Mauve", "hex": "#E0B4D6", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-mauve-magic", "price": "₹149"},
            {"name": "Classic French Pink", "hex": "#FFB6C1", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-pink-dreams", "price": "₹149"},
            {"name": "Light Berry", "hex": "#DA70D6", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-berry-bliss", "price": "₹149"},
        ]
    },
    "light_medium_specific": {
        "display_name": "🍑 Perfect for Light-Medium Skin",
        "colors": [
            {"name": "Warm Terracotta", "hex": "#E2725B", "link": "https://www.sugarcosmetics.com/products/tip-tac-toe-nail-lacquer-terracotta-dream", "price": "₹299"},
            {"name": "Golden Coral", "hex": "#FF6347", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-coral-vibes", "price": "₹149"},
            {"name": "Warm Nude", "hex": "#D2B48C", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-caramel-crush", "price": "₹149"},
            {"name": "Sunset Orange", "hex": "#FF8C69", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-sunset-vibes", "price": "₹149"},
            {"name": "Rose Gold", "hex": "#E8B4B8", "link": "https://www.sugarcosmetics.com/products/tip-tac-toe-nail-lacquer-rose-gold", "price": "₹299"},
        ]
    },
    "medium_specific": {
        "display_name": "🌿 Perfect for Medium Skin",
        "colors": [
            {"name": "Rich Burgundy", "hex": "#800020", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-burgundy-beauty", "price": "₹149"},
            {"name": "Deep Coral", "hex": "#FF5722", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-deep-coral", "price": "₹149"},
            {"name": "Olive Green", "hex": "#808000", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-olive-branch", "price": "₹149"},
            {"name": "Warm Brown", "hex": "#8B4513", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-chocolate-truffle", "price": "₹149"},
            {"name": "Copper Glow", "hex": "#B87333", "link": "https://www.sugarcosmetics.com/products/tip-tac-toe-nail-lacquer-copper-penny", "price": "₹299"},
        ]
    },
    "medium_dark_specific": {
        "display_name": "✨ Perfect for Medium-Dark Skin",
        "colors": [
            {"name": "Electric Purple", "hex": "#8A2BE2", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-purple-rain", "price": "₹149"},
            {"name": "Vibrant Teal", "hex": "#008B8B", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-teal-magic", "price": "₹149"},
            {"name": "Hot Magenta", "hex": "#FF1493", "link": "https://www.sugarcosmetics.com/products/tip-tac-toe-nail-lacquer-hot-pink", "price": "₹299"},
            {"name": "Golden Yellow", "hex": "#FFD700", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-yellow-mellow", "price": "₹149"},
            {"name": "Bold Orange", "hex": "#FF4500", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-orange-crush", "price": "₹149"},
        ]
    },
    "dark_specific": {
        "display_name": "🔥 Perfect for Dark Skin",
        "colors": [
            {"name": "Electric Lime", "hex": "#CCFF00", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-neon-lime", "price": "₹149"},
            {"name": "Bright Fuchsia", "hex": "#FF00FF", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-fuchsia-fever", "price": "₹149"},
            {"name": "Royal Blue", "hex": "#4169E1", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-royal-blue", "price": "₹149"},
            {"name": "Gold Chrome", "hex": "#FFD700", "link": "https://www.sugarcosmetics.com/products/sugar-pop-glitter-nail-lacquer-gold-dust", "price": "₹199"},
            {"name": "Silver Metallic", "hex": "#C0C0C0", "link": "https://www.sugarcosmetics.com/products/sugar-pop-glitter-nail-lacquer-silver-shine", "price": "₹199"},
        ]
    },
    "very_dark_specific": {
        "display_name": "💎 Perfect for Very Dark Skin",
        "colors": [
            {"name": "Neon Pink", "hex": "#FF6EC7", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-neon-pink", "price": "₹149"},
            {"name": "Electric Blue", "hex": "#00FFFF", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-electric-blue", "price": "₹149"},
            {"name": "Holographic Silver", "hex": "#E0E0E0", "link": "https://www.sugarcosmetics.com/products/sugar-pop-glitter-nail-lacquer-holographic", "price": "₹199"},
            {"name": "Bright White", "hex": "#FFFFFF", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-pure-white", "price": "₹149"},
            {"name": "Neon Green", "hex": "#39FF14", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-neon-green", "price": "₹149"},
        ]
    },
    # Universal categories for general browsing
    "classic_reds": {
        "display_name": "❤️ Classic Reds",
        "colors": [
            {"name": "Cherry Pop", "hex": "#DC143C", "link": "https://www.sugarcosmetics.com/products/tip-tac-toe-nail-lacquer-cherry-on-top", "price": "₹299"},
            {"name": "Ruby Red", "hex": "#E0115F", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-ruby-tuesday", "price": "₹149"},
            {"name": "Crimson Glory", "hex": "#B22222", "link": "https://www.sugarcosmetics.com/products/tip-tac-toe-nail-lacquer-crimson-classic", "price": "₹299"},
            {"name": "Wine Berry", "hex": "#722F37", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-wine-down", "price": "₹149"},
        ]
    },
    "nude_collection": {
        "display_name": "🤎 Nude Collection",
        "colors": [
            {"name": "Barely There Nude", "hex": "#F5E6D3", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer", "price": "₹149"},
            {"name": "Warm Taupe", "hex": "#D4B5A0", "link": "https://www.sugarcosmetics.com/products/tip-tac-toe-nail-lacquer-social-sepia", "price": "₹299"},
            {"name": "Caramel Kiss", "hex": "#D2B48C", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-caramel-crush", "price": "₹149"},
            {"name": "Mocha Cream", "hex": "#C8A882", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-coffee-break", "price": "₹149"},
        ]
    },
    "metallics_glitter": {
        "display_name": "✨ Metallics & Glitter",
        "colors": [
            {"name": "Rose Gold Glam", "hex": "#E8B4B8", "link": "https://www.sugarcosmetics.com/products/tip-tac-toe-nail-lacquer-rose-gold-glitter", "price": "₹299"},
            {"name": "Gold Rush", "hex": "#FFD700", "link": "https://www.sugarcosmetics.com/products/sugar-pop-glitter-nail-lacquer-gold-dust", "price": "₹199"},
            {"name": "Silver Storm", "hex": "#C0C0C0", "link": "https://www.sugarcosmetics.com/products/sugar-pop-glitter-nail-lacquer-silver-shine", "price": "₹199"},
            {"name": "Holographic Magic", "hex": "#E0E0E0", "link": "https://www.sugarcosmetics.com/products/sugar-pop-glitter-nail-lacquer-holographic", "price": "₹199"},
        ]
    }
}

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

def detect_hands_mediapipe(image):
    """Use MediaPipe to detect hand landmarks and extract hand regions"""
    with mp_hands.Hands(
        static_image_mode=True,
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as hands:
        
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) if len(image.shape) == 3 else image
        results = hands.process(rgb_image)
        
        hand_regions = []
        if results.multi_hand_landmarks:
            h, w = image.shape[:2]
            for hand_landmarks in results.multi_hand_landmarks:
                # Get bounding box of hand
                x_coords = [landmark.x * w for landmark in hand_landmarks.landmark]
                y_coords = [landmark.y * h for landmark in hand_landmarks.landmark]
                
                x_min, x_max = int(min(x_coords)), int(max(x_coords))
                y_min, y_max = int(min(y_coords)), int(max(y_coords))
                
                # Add padding
                padding = 20
                x_min = max(0, x_min - padding)
                y_min = max(0, y_min - padding)
                x_max = min(w, x_max + padding)
                y_max = min(h, y_max + padding)
                
                hand_regions.append((x_min, y_min, x_max, y_max))
        
        return hand_regions

def extract_skin_color_advanced(image):
    """Advanced skin color extraction using multiple methods"""
    if len(image.shape) == 3 and image.shape[2] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
    elif len(image.shape) == 3 and image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    
    # Method 1: MediaPipe hand detection
    hand_regions = detect_hands_mediapipe(image)
    
    if hand_regions:
        # Extract color from detected hand regions
        all_skin_pixels = []
        for x_min, y_min, x_max, y_max in hand_regions:
            hand_roi = image[y_min:y_max, x_min:x_max]
            
            # Apply skin detection in the hand region
            skin_mask = detect_skin_regions_improved(cv2.cvtColor(hand_roi, cv2.COLOR_BGR2RGB))
            if np.sum(skin_mask) > 100:  # Ensure we have enough skin pixels
                skin_pixels = hand_roi[skin_mask > 0]
                if len(skin_pixels) > 0:
                    all_skin_pixels.extend(skin_pixels)
        
        if all_skin_pixels:
            all_skin_pixels = np.array(all_skin_pixels)
            # Use median for more robust color estimation
            avg_color_bgr = np.median(all_skin_pixels, axis=0).astype(int)
            avg_color_rgb = avg_color_bgr[::-1]  # Convert BGR to RGB
            return avg_color_rgb, True
    
    # Method 2: Fallback to original method
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    avg_color, skin_mask = extract_hand_skin_color_improved(rgb_image)
    if avg_color is not None:
        return avg_color, True
    
    return None, False

def detect_skin_regions_improved(image, sensitivity=5):
    """Improved skin detection using multiple color spaces"""
    # YCrCb color space detection
    ycrcb = cv2.cvtColor(image, cv2.COLOR_RGB2YCR_CB)
    lower_skin_ycrcb = np.array([0, 125, 70], dtype=np.uint8)
    upper_skin_ycrcb = np.array([255, 185, 135], dtype=np.uint8)
    mask_ycrcb = cv2.inRange(ycrcb, lower_skin_ycrcb, upper_skin_ycrcb)
    
    # HSV color space detection
    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    lower_hsv1 = np.array([0, 20, 50], dtype=np.uint8)
    upper_hsv1 = np.array([20, 150, 255], dtype=np.uint8)
    mask_hsv1 = cv2.inRange(hsv, lower_hsv1, upper_hsv1)
    
    lower_hsv2 = np.array([0, 20, 20], dtype=np.uint8)
    upper_hsv2 = np.array([25, 180, 200], dtype=np.uint8)
    mask_hsv2 = cv2.inRange(hsv, lower_hsv2, upper_hsv2)
    
    # RGB color space detection for additional coverage
    r, g, b = cv2.split(image)
    mask_rgb = ((r > 95) & (g > 40) & (b > 20) & 
                ((np.maximum(r, np.maximum(g, b)) - np.minimum(r, np.minimum(g, b))) > 15) &
                (np.abs(r.astype(int) - g.astype(int)) > 15) & 
                (r > g) & (r > b)).astype(np.uint8) * 255
    
    # Combine all masks
    combined_mask = cv2.bitwise_or(mask_ycrcb, mask_hsv1)
    combined_mask = cv2.bitwise_or(combined_mask, mask_hsv2)
    combined_mask = cv2.bitwise_or(combined_mask, mask_rgb)
    
    # Morphological operations for noise reduction
    kernel_size = max(3, sensitivity)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
    combined_mask = cv2.medianBlur(combined_mask, 5)
    
    return combined_mask

def extract_hand_skin_color_improved(image, sensitivity=5):
    """Improved hand skin color extraction"""
    skin_mask = detect_skin_regions_improved(image, sensitivity)
    
    # Find contours
    contours, _ = cv2.findContours(skin_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None, None
    
    # Filter contours by area
    min_area = (image.shape[0] * image.shape[1]) * 0.01
    large_contours = [c for c in contours if cv2.contourArea(c) > min_area]
    
    if not large_contours:
        large_contours = [max(contours, key=cv2.contourArea)]
    
    # Get the largest contour (likely the hand)
    largest_contour = max(large_contours, key=cv2.contourArea)
    
    # Create mask for the hand
    hand_mask = np.zeros_like(skin_mask)
    cv2.fillPoly(hand_mask, [largest_contour], 255)
    
    # Extract hand pixels
    hand_pixels = image[hand_mask > 0]
    
    if len(hand_pixels) > 100:
        # Use median for more robust color estimation
        avg_color = np.median(hand_pixels, axis=0).astype(int)
        return avg_color, hand_mask
    
    return None, None

def analyze_skin_tone_advanced(rgb_color):
    """Enhanced skin tone analysis with more precise categorization"""
    r, g, b = rgb_color
    
    # Convert to different color spaces for analysis
    bgr_color = np.array([[[b, g, r]]], dtype=np.uint8)
    lab = cv2.cvtColor(bgr_color, cv2.COLOR_BGR2LAB)[0][0]
    hsv = cv2.cvtColor(bgr_color, cv2.COLOR_BGR2HSV)[0][0]
    
    l, a, b_lab = lab.astype(float)
    h, s, v = hsv.astype(float)
    
    # Normalize RGB values
    r_norm, g_norm, b_norm = r/255.0, g/255.0, b/255.0
    
    # ITA (Individual Typology Angle) calculation
    ita = np.degrees(np.arctan2(b_lab - 50, l - 50)) if l != 50 else 0
    
    # Additional metrics
    brightness = (r + g + b) / 3.0
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    
    # Skin undertone analysis
    red_yellow_ratio = r / (g + 1e-6)
    red_blue_ratio = r / (b + 1e-6)
    yellow_blue_ratio = g / (b + 1e-6)
    
    # Melanin index approximation
    melanin_index = 100 * np.log10((1/r_norm + 1e-6) / (1/g_norm + 1e-6))
    
    print(f"Debug - RGB: ({r}, {g}, {b})")
    print(f"Debug - L*a*b*: ({l:.1f}, {a:.1f}, {b_lab:.1f})")
    print(f"Debug - ITA: {ita:.1f}")
    print(f"Debug - Brightness: {brightness:.1f}")
    print(f"Debug - Luminance: {luminance:.1f}")
    print(f"Debug - Melanin Index: {melanin_index:.1f}")
    
    # Enhanced classification with more precise boundaries
    
    # Very Light Skin (Fitzpatrick I-II)
    if (ita > 55 and l > 75 and luminance > 200) or \
       (brightness > 200 and red_yellow_ratio > 1.1 and melanin_index < -20):
        return "very_light"
    
    # Light Skin (Fitzpatrick II-III) 
    elif (ita > 41 and l > 65 and luminance > 160) or \
         (brightness > 170 and brightness <= 200 and red_yellow_ratio > 1.05):
        return "light"
    
    # Light-Medium Skin
    elif (ita > 28 and l > 55 and luminance > 140) or \
         (brightness > 140 and brightness <= 170 and yellow_blue_ratio > 1.1):
        return "light_medium"
    
    # Medium Skin (Fitzpatrick III-IV)
    elif (ita > 15 and l > 45 and luminance > 110) or \
         (brightness > 110 and brightness <= 140 and melanin_index > -10):
        return "medium"
    
    # Medium-Dark Skin (Fitzpatrick IV-V)
    elif (ita > 2 and l > 35 and luminance > 80) or \
         (brightness > 80 and brightness <= 110 and melanin_index > 0):
        return "medium_dark"
    
    # Dark Skin (Fitzpatrick V)
    elif (ita > -15 and l > 25 and luminance > 50) or \
         (brightness > 50 and brightness <= 80):
        return "dark"
    
    # Very Dark Skin (Fitzpatrick VI)
    else:
        return "very_dark"

def get_color_recommendations(skin_tone):
    """Get highly specific and diverse color recommendations based on skin tone"""
    
    # Skin tone specific recommendations with completely different color palettes
    recommendations = {
        "very_light": {
            "primary": [f"{skin_tone}_specific"],
            "secondary": ["classic_reds", "metallics_glitter"],
            "avoid": ["medium_dark_specific", "dark_specific", "very_dark_specific"],
            "description": "Cool-toned pastels and delicate shades enhance your porcelain complexion beautifully! Soft pinks and lavenders are your perfect match.",
            "tips": "Avoid overly warm or neon shades that might clash with your cool undertones."
        },
        
        "light": {
            "primary": [f"{skin_tone}_specific"],
            "secondary": ["nude_collection"],
            "avoid": ["very_dark_specific"],
            "description": "Peachy corals and soft mauves complement your fair skin perfectly! You can wear both cool and warm tones beautifully.",
            "tips": "Peach and coral tones bring out your natural warmth, while soft berries add elegance."
        },
        
        "light_medium": {
            "primary": [f"{skin_tone}_specific"],
            "secondary": ["classic_reds"],
            "avoid": ["very_light_specific"],
            "description": "Warm earth tones and golden hues are stunning on you! Terracotta and sunset shades bring out your natural glow.",
            "tips": "Embrace warm undertones with golden corals, terracotta, and rose gold shades."
        },
        
        "medium": {
            "primary": [f"{skin_tone}_specific"],
            "secondary": ["metallics_glitter"],
            "avoid": ["very_light_specific"],
            "description": "Rich jewel tones and earthy shades showcase your beautiful complexion! Deep burgundy and olive greens are particularly striking.",
            "tips": "You can pull off both warm and cool deep tones. Try burgundy, forest green, and copper."
        },
        
        "medium_dark": {
            "primary": [f"{skin_tone}_specific"],
            "secondary": ["classic_reds"],
            "avoid": ["very_light_specific", "light_specific"],
            "description": "Bold, vibrant colors pop beautifully against your skin! Electric purples and bright teals are absolutely stunning on you.",
            "tips": "Don't shy away from bright, saturated colors - they were made for your skin tone!"
        },
        
        "dark": {
            "primary": [f"{skin_tone}_specific"],
            "secondary": ["metallics_glitter"],
            "avoid": ["very_light_specific", "light_specific", "nude_collection"],
            "description": "Bright neons and metallic shades create gorgeous contrast on your rich complexion! Electric lime and bright fuchsia are show-stoppers.",
            "tips": "Bright, bold colors and metallics look incredible on you. Try neon greens, electric blues, and gold chrome."
        },
        
        "very_dark": {
            "primary": [f"{skin_tone}_specific"],
            "secondary": [],
            "avoid": ["very_light_specific", "light_specific", "light_medium_specific", "nude_collection"],
            "description": "Vibrant neons and high-contrast shades are absolutely magical on your deep, rich skin! Neon pink and electric blue create stunning drama.",
            "tips": "You can wear the boldest, brightest colors beautifully. Neons, pure white, and holographic shades are perfect!"
        }
    }
    
    return recommendations.get(skin_tone, {
        "primary": ["classic_reds"],
        "secondary": ["metallics_glitter"],
        "avoid": [],
        "description": "Classic shades that work beautifully on your unique skin tone!",
        "tips": "Experiment with different shades to find your perfect match."
    })

def create_color_card(color_info):
    """Create a styled color card"""
    return f"""
    <div style="margin: 10px 0; display: flex; justify-content: space-between; align-items: center; background: linear-gradient(135deg, #fff5f7 0%, #f8f9fa 100%); padding: 12px; border-radius: 12px; box-shadow: 0 3px 8px rgba(0,0,0,0.1); border: 1px solid rgba(255,105,180,0.2);">
        <div style="display: flex; align-items: center;">
            <div style="width: 25px; height: 25px; background-color: {color_info['hex']}; border-radius: 50%; margin-right: 12px; border: 2px solid #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.2);"></div>
            <a href="{color_info['link']}" target="_blank" style="color: #FF69B4; text-decoration: none; font-family: 'Arial', sans-serif; font-size: 1.1em; font-weight: 600;">{color_info['name']} ✨</a>
        </div>
        <span style="color: #333; font-weight: bold; background: rgba(255,215,0,0.2); padding: 4px 8px; border-radius: 8px;">{color_info['price']} 💎</span>
    </div>
    """

def main():
    st.set_page_config(page_title="💅 Personalized Nail Polish Advisor", page_icon="💅", layout="wide")
    
    # Custom CSS with enhanced styling
    st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #fff5f7 0%, #ffe6f0 50%, #f0e6f0 100%);
        min-height: 100vh;
    }
    .header {
        text-align: center;
        color: #000;
        font-size: 3.2em;
        font-family: 'Georgia', serif;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        animation: fadeIn 2s ease-in-out;
        margin-bottom: 10px;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .subheader {
        text-align: center;
        color: #555;
        font-style: italic;
        font-family: 'Arial', sans-serif;
        margin-bottom: 30px;
        animation: float 3s infinite ease-in-out;
        font-size: 1.2em;
    }
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
    }
    .recommendation-section {
        background: linear-gradient(135deg, rgba(255, 245, 247, 0.95) 0%, rgba(248, 249, 250, 0.95) 100%);
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        animation: slideIn 1s ease-out;
        position: relative;
        border: 1px solid rgba(255,105,180,0.2);
    }
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(50px); }
        to { opacity: 1; transform: translateX(0); }
    }
    .left-column {
        background: linear-gradient(135deg, #fffaf0 0%, #fff5f5 100%);
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,105,180,0.1);
    }
    .skin-tone-display {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 15px 0;
        border-left: 5px solid #FF69B4;
        box-shadow: 0 3px 10px rgba(0,0,0,0.1);
    }
    .tips-section {
        background: linear-gradient(135deg, rgba(255,215,0,0.1) 0%, rgba(255,192,203,0.1) 100%);
        padding: 15px;
        border-radius: 12px;
        margin: 15px 0;
        border: 1px solid rgba(255,215,0,0.3);
    }
    .avoid-section {
        background: linear-gradient(135deg, rgba(255,99,71,0.1) 0%, rgba(255,182,193,0.1) 100%);
        padding: 15px;
        border-radius: 12px;
        margin: 15px 0;
        border: 1px solid rgba(255,99,71,0.3);
    }
    .category-header {
        color: #333;
        font-size: 1.3em;
        font-weight: 600;
        margin: 20px 0 10px 0;
        padding: 10px;
        background: linear-gradient(90deg, rgba(255,105,180,0.1) 0%, rgba(255,105,180,0.05) 100%);
        border-radius: 8px;
        border-left: 4px solid #FF69B4;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 class="header">💅 Personalized Nail Polish Advisor</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subheader">Discover your perfect shade with AI-powered skin tone analysis! Each skin tone gets unique recommendations! 🌹✨</p>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<div class="left-column">', unsafe_allow_html=True)
        st.header("📸 Capture Your Elegance")
        
        # Analysis method selection
        st.subheader("🔬 Analysis Method")
        analysis_method = st.selectbox(
            "Choose analysis method:",
            ["Advanced AI Detection (Recommended)", "Traditional Color Analysis"],
            help="Advanced AI uses MediaPipe for better hand detection and skin tone analysis"
        )
        
        input_method = st.radio("Choose your style:", ["📷 Camera", "📁 Upload Photo"], horizontal=True)
        
        uploaded_image = None
        if input_method == "📷 Camera":
            uploaded_image = st.camera_input("📸 Snap a chic hand photo, love! 💕")
        else:
            uploaded_image = st.file_uploader("📁 Upload a glamorous hand image", type=['png', 'jpg', 'jpeg'])
        
        if uploaded_image is not None:
            image = Image.open(uploaded_image)
            st.image(image, caption="Your beautiful hand! 💫", use_container_width=True)
            
            # Convert PIL image to numpy array
            image_array = np.array(image)
            
            if len(image_array.shape) == 3:
                with st.spinner("🔍 Analyzing your unique skin tone with AI..."):
                    try:
                        if analysis_method == "Advanced AI Detection (Recommended)":
                            avg_color, success = extract_skin_color_advanced(image_array)
                            if success:
                                skin_tone = analyze_skin_tone_advanced(avg_color)
                            else:
                                success = False
                        else:
                            # Fallback to traditional method
                            if len(image_array.shape) == 4:
                                image_array = cv2.cvtColor(image_array, cv2.COLOR_RGBA2RGB)
                            avg_color, _ = extract_hand_skin_color_improved(image_array)
                            if avg_color is not None:
                                skin_tone = analyze_skin_tone_advanced(avg_color)
                                success = True
                            else:
                                success = False
                        
                        if success:
                            # Display skin tone analysis
                            st.markdown(f"""
                            <div class="skin-tone-display">
                                <h4>✨ Advanced Skin Tone Analysis</h4>
                                <p><strong>Detected Tone:</strong> {skin_tone.replace('_', ' ').title()}</p>
                                <p><strong>RGB Values:</strong> R:{avg_color[0]}, G:{avg_color[1]}, B:{avg_color[2]}</p>
                                <div style="width: 60px; height: 60px; background-color: rgb({avg_color[0]}, {avg_color[1]}, {avg_color[2]}); border-radius: 50%; margin: 10px 0; border: 3px solid #fff; box-shadow: 0 3px 8px rgba(0,0,0,0.3); display: inline-block;"></div>
                                <p style="margin-top: 10px;"><em>Analysis based on scientific color theory and Fitzpatrick scale</em></p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Get recommendations
                            recommendations = get_color_recommendations(skin_tone)
                            
                            # Show recommendations
                            with col2:
                                st.markdown('<div class="recommendation-section">', unsafe_allow_html=True)
                                st.markdown("## 🎀 Your Personalized Recommendations")
                                st.markdown(f'<p style="text-align: center; color: #333; font-style: italic; font-size: 1.1em; margin-bottom: 20px;">"{recommendations["description"]}"</p>', unsafe_allow_html=True)
                                
                                # Expert tips section
                                if "tips" in recommendations:
                                    st.markdown(f"""
                                    <div class="tips-section">
                                        <h4>💡 Expert Tips for Your Skin Tone</h4>
                                        <p>{recommendations["tips"]}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                # Primary recommendations - skin tone specific
                                st.markdown('<div class="category-header">🌟 Perfect Matches - Curated Just For You!</div>', unsafe_allow_html=True)
                                for category_key in recommendations["primary"]:
                                    if category_key in COMPREHENSIVE_COLOR_PALETTE:
                                        category_data = COMPREHENSIVE_COLOR_PALETTE[category_key]
                                        st.markdown(f"#### {category_data['display_name']}")
                                        for color_info in category_data["colors"]:
                                            st.markdown(create_color_card(color_info), unsafe_allow_html=True)
                                
                                # Secondary recommendations
                                if recommendations["secondary"]:
                                    st.markdown('<div class="category-header">✨ Great Alternatives - Also Beautiful On You!</div>', unsafe_allow_html=True)
                                    for category_key in recommendations["secondary"]:
                                        if category_key in COMPREHENSIVE_COLOR_PALETTE:
                                            category_data = COMPREHENSIVE_COLOR_PALETTE[category_key]
                                            st.markdown(f"#### {category_data['display_name']}")
                                            # Show only first 3 colors from secondary categories to avoid overwhelming
                                            for color_info in category_data["colors"][:3]:
                                                st.markdown(create_color_card(color_info), unsafe_allow_html=True)
                                

                                
                                st.markdown('</div>', unsafe_allow_html=True)
                        else:
                            st.error("❌ Couldn't detect your hand clearly. Please try:")
                            st.markdown("""
                            - Better lighting (natural light works best)
                            - Clear hand visibility 
                            - Steady camera position
                            - Avoid shadows on your hand 🌸
                            """)
                    
                    except Exception as e:
                        st.error(f"❌ Analysis failed: {str(e)}")
                        st.info("💡 Try the Traditional Color Analysis method or upload a different image.")
            else:
                st.error("❌ Please upload a colorful image, dear! 🎨")
        else:
            with col2:
                st.markdown('<div class="recommendation-section">', unsafe_allow_html=True)
                st.markdown("## 🌺 Complete Nail Polish Collection")
                st.markdown('<p style="text-align: center; color: #333; font-size: 1.1em;">Explore every luxurious shade in our collection! Upload your photo to get personalized recommendations! 💄</p>', unsafe_allow_html=True)
                
                # Show universal categories when no image is uploaded
                st.markdown('<div class="category-header">❤️ Timeless Classics</div>', unsafe_allow_html=True)
                for color_info in COMPREHENSIVE_COLOR_PALETTE["classic_reds"]["colors"]:
                    st.markdown(create_color_card(color_info), unsafe_allow_html=True)
                
                st.markdown('<div class="category-header">🤎 Versatile Nudes</div>', unsafe_allow_html=True)
                for color_info in COMPREHENSIVE_COLOR_PALETTE["nude_collection"]["colors"]:
                    st.markdown(create_color_card(color_info), unsafe_allow_html=True)
                
                st.markdown('<div class="category-header">✨ Glamorous Metallics</div>', unsafe_allow_html=True)
                for color_info in COMPREHENSIVE_COLOR_PALETTE["metallics_glitter"]["colors"]:
                    st.markdown(create_color_card(color_info), unsafe_allow_html=True)
                
                # Call to action
                st.markdown("""
                <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, rgba(255,105,180,0.1) 0%, rgba(255,182,193,0.1) 100%); border-radius: 15px; margin: 20px 0;">
                    <h3 style="color: #FF69B4;">📸 Ready for Your Personal Recommendations?</h3>
                    <p>Upload a photo of your hand to discover colors specifically chosen for your unique skin tone!</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Enhanced information section
        st.markdown("---")
        st.markdown("### 🎨 About Our Skin Tone Analysis")
        st.markdown("""
        **Our Advanced AI System Analyzes:**
        - 🤖 **MediaPipe Hand Detection** - Precisely locates your hand
        - 🎯 **Multi-Region Color Extraction** - Samples from multiple skin areas
        - 🔬 **Advanced Color Space Analysis** - RGB, HSV, and LAB color spaces
        - 📊 **ITA Calculation** - Individual Typology Angle for scientific accuracy
        - 🧬 **Melanin Index Estimation** - For precise undertone analysis
        
        **Each Skin Tone Gets Unique Recommendations:**
        - **Very Light** → Cool pastels and delicate shades
        - **Light** → Peachy corals and soft tones  
        - **Light-Medium** → Warm earth tones and golden hues
        - **Medium** → Rich jewel tones and deep colors
        - **Medium-Dark** → Bold, vibrant and electric shades
        - **Dark** → Bright neons and metallic contrasts
        - **Very Dark** → High-contrast neons and dramatic colors
        """)
        
        with st.expander("📋 Tips for Best Results"):
            st.markdown("""
            **For Optimal Analysis:**
            - 🌞 Use natural daylight when possible
            - 🤚 Show your palm or back of hand clearly
            - 📱 Keep camera steady and close enough
            - 🚫 Avoid harsh artificial lighting
            - 💄 Remove any existing nail polish
            - 🖐️ Spread fingers slightly apart
            
            **Why Different Recommendations?**
            Each skin tone has unique undertones that complement different colors. Our AI considers:
            - Warm vs. cool undertones
            - Color contrast ratios
            - Melanin levels
            - Scientific color theory
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Enhanced footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 25px; background: linear-gradient(135deg, rgba(255,245,247,0.8) 0%, rgba(240,230,240,0.8) 100%); border-radius: 15px; margin: 20px 0;">
        <h3 style="color: #FF69B4;">✨ Powered by AI & Science ✨</h3>
        <p style="color: #666; font-size: 1.1em;">Each skin tone deserves its own perfect palette</p>
        <p>💅 Shop your personalized recommendations at <a href="https://www.sugarcosmetics.com" target="_blank" style="color: #FF69B4; font-weight: bold;">Sugar Cosmetics</a> 💅</p>
        <p style="font-size: 0.9em; color: #888; margin-top: 15px;">Advanced color matching using MediaPipe AI, LAB color space analysis, and dermatological science</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
