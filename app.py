import streamlit as st
import cv2
import numpy as np
from PIL import Image

# Comprehensive color palette with real Sugar Cosmetics products and links
COMPREHENSIVE_COLOR_PALETTE = {
    "nude_light": {
        "display_name": "🌸 Light Nudes",
        "colors": [
            {"name": "Barely There Nude", "hex": "#F5E6D3", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer", "price": "₹149"},
            {"name": "Pearl Pink", "hex": "#F8E8E7", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-50-pearl-pink", "price": "₹149"},
            {"name": "Champagne Shimmer", "hex": "#F7E7CE", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-glitter-01-rose-quartz", "price": "₹199"},
            {"name": "Soft Beige", "hex": "#F0E5D0", "link": "https://www.sugarcosmetics.com/products/tip-tac-toe-nail-lacquer-beige-basic", "price": "₹299"},
        ]
    },
    "nude_medium": {
        "display_name": "🤎 Medium Nudes",
        "colors": [
            {"name": "Warm Taupe", "hex": "#D4B5A0", "link": "https://www.sugarcosmetics.com/products/tip-tac-toe-nail-lacquer-social-sepia", "price": "₹299"},
            {"name": "Caramel Kiss", "hex": "#D2B48C", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-caramel-crush", "price": "₹149"},
            {"name": "Dusty Rose", "hex": "#D4A5A5", "link": "https://www.sugarcosmetics.com/products/tip-tac-toe-nail-lacquer-rose-gold", "price": "₹299"},
            {"name": "Mocha Cream", "hex": "#C8A882", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-coffee-break", "price": "₹149"},
        ]
    },
    "light_pastels": {
        "display_name": "🌈 Light Pastels",
        "colors": [
            {"name": "Soft Lavender", "hex": "#E6E6FA", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-lavender-love", "price": "₹149"},
            {"name": "Mint Fresh", "hex": "#F0FFF0", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-mint-to-be", "price": "₹149"},
            {"name": "Baby Blue", "hex": "#E0F6FF", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-sky-high", "price": "₹149"},
            {"name": "Peach Whisper", "hex": "#FFDBAC", "link": "https://www.sugarcosmetics.com/products/tip-tac-toe-nail-lacquer-peach-please", "price": "₹299"},
            {"name": "Cotton Candy", "hex": "#FFB6C1", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-pink-dreams", "price": "₹149"},
        ]
    },
    "medium_brights": {
        "display_name": "🔥 Medium Brights",
        "colors": [
            {"name": "Coral Crush", "hex": "#FF7F50", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-coral-vibes", "price": "₹149"},
            {"name": "Rose Garden", "hex": "#FF69B4", "link": "https://www.sugarcosmetics.com/products/tip-tac-toe-nail-lacquer-hot-pink", "price": "₹299"},
            {"name": "Sunshine Yellow", "hex": "#FFD700", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-yellow-mellow", "price": "₹149"},
            {"name": "Ocean Blue", "hex": "#4169E1", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-ocean-blues", "price": "₹149"},
            {"name": "Fresh Green", "hex": "#32CD32", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-green-machine", "price": "₹149"},
        ]
    },
    "classic_reds": {
        "display_name": "❤️ Classic Reds",
        "colors": [
            {"name": "Cherry Pop", "hex": "#DC143C", "link": "https://www.sugarcosmetics.com/products/tip-tac-toe-nail-lacquer-cherry-on-top", "price": "₹299"},
            {"name": "Ruby Red", "hex": "#E0115F", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-ruby-tuesday", "price": "₹149"},
            {"name": "Crimson Glory", "hex": "#B22222", "link": "https://www.sugarcosmetics.com/products/tip-tac-toe-nail-lacquer-crimson-classic", "price": "₹299"},
            {"name": "Wine Berry", "hex": "#722F37", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-wine-down", "price": "₹149"},
        ]
    },
    "deep_darks": {
        "display_name": "🖤 Deep Darks",
        "colors": [
            {"name": "Midnight Black", "hex": "#000000", "link": "https://www.sugarcosmetics.com/products/tip-tac-toe-nail-lacquer-black-swan", "price": "₹299"},
            {"name": "Navy Dreams", "hex": "#191970", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-navy-blue", "price": "₹149"},
            {"name": "Forest Night", "hex": "#355E3B", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-forest-green", "price": "₹149"},
            {"name": "Plum Perfect", "hex": "#8B008B", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-purple-rain", "price": "₹149"},
            {"name": "Chocolate Brown", "hex": "#7B3F00", "link": "https://www.sugarcosmetics.com/products/sugar-pop-nail-lacquer-chocolate-truffle", "price": "₹149"},
        ]
    },
    "metallics_glitter": {
        "display_name": "✨ Metallics & Glitter",
        "colors": [
            {"name": "Rose Gold Glam", "hex": "#E8B4B8", "link": "https://www.sugarcosmetics.com/products/tip-tac-toe-nail-lacquer-rose-gold-glitter", "price": "₹299"},
            {"name": "Gold Rush", "hex": "#FFD700", "link": "https://www.sugarcosmetics.com/products/sugar-pop-glitter-nail-lacquer-gold-dust", "price": "₹199"},
            {"name": "Silver Storm", "hex": "#C0C0C0", "link": "https://www.sugarcosmetics.com/products/sugar-pop-glitter-nail-lacquer-silver-shine", "price": "₹199"},
            {"name": "Copper Shine", "hex": "#B87333", "link": "https://www.sugarcosmetics.com/products/tip-tac-toe-nail-lacquer-copper-penny", "price": "₹299"},
            {"name": "Holographic Magic", "hex": "#E0E0E0", "link": "https://www.sugarcosmetics.com/products/sugar-pop-glitter-nail-lacquer-holographic", "price": "₹199"},
        ]
    }
}

def detect_skin_regions_improved(image, sensitivity=5):
    ycrcb = cv2.cvtColor(image, cv2.COLOR_RGB2YCR_CB)
    lower_skin_ycrcb = np.array([0, 125, 70], dtype=np.uint8)
    upper_skin_ycrcb = np.array([255, 185, 135], dtype=np.uint8)
    mask_ycrcb = cv2.inRange(ycrcb, lower_skin_ycrcb, upper_skin_ycrcb)
    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    lower_hsv1 = np.array([0, 20, 50], dtype=np.uint8)
    upper_hsv1 = np.array([20, 150, 255], dtype=np.uint8)
    mask_hsv1 = cv2.inRange(hsv, lower_hsv1, upper_hsv1)
    lower_hsv2 = np.array([0, 20, 20], dtype=np.uint8)
    upper_hsv2 = np.array([25, 180, 200], dtype=np.uint8)
    mask_hsv2 = cv2.inRange(hsv, lower_hsv2, upper_hsv2)
    combined_mask = cv2.bitwise_or(mask_ycrcb, mask_hsv1)
    combined_mask = cv2.bitwise_or(combined_mask, mask_hsv2)
    kernel_size = max(3, sensitivity)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
    combined_mask = cv2.medianBlur(combined_mask, 5)
    return combined_mask

def extract_hand_skin_color_improved(image, sensitivity=5):
    skin_mask = detect_skin_regions_improved(image, sensitivity)
    contours, _ = cv2.findContours(skin_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None, None
    min_area = (image.shape[0] * image.shape[1]) * 0.01
    large_contours = [c for c in contours if cv2.contourArea(c) > min_area]
    if not large_contours:
        large_contours = [max(contours, key=cv2.contourArea)]
    largest_contour = max(large_contours, key=cv2.contourArea)
    hand_mask = np.zeros_like(skin_mask)
    cv2.fillPoly(hand_mask, [largest_contour], 255)
    hand_pixels = image[hand_mask > 0]
    if len(hand_pixels) > 100:
        avg_color = np.median(hand_pixels, axis=0).astype(int)
        return avg_color, hand_mask
    return None, None

def analyze_skin_tone_improved(rgb_color):
    r, g, b = rgb_color
    bgr_color = np.array([[[b, g, r]]], dtype=np.uint8)
    lab = cv2.cvtColor(bgr_color, cv2.COLOR_BGR2LAB)[0][0]
    l, a, b_lab = lab
    ita = np.arctan2(b_lab - 50, l - 50) * 180 / np.pi if l != 50 else 0
    if ita > 55 and l > 70:
        return "very_light"
    elif ita > 41 and l > 60:
        return "light"
    elif ita > 28 and l > 45:
        return "medium"
    elif ita > 10 and l > 30:
        return "dark"
    else:
        return "very_dark"

def get_color_recommendations(skin_tone):
    recommendations = {
        "very_light": ["nude_light", "light_pastels", "classic_reds", "metallics_glitter"],
        "light": ["nude_light", "nude_medium", "light_pastels", "medium_brights", "classic_reds"],
        "medium": ["nude_medium", "medium_brights", "classic_reds", "deep_darks", "metallics_glitter"],
        "dark": ["nude_medium", "medium_brights", "classic_reds", "deep_darks", "metallics_glitter"],
        "very_dark": ["medium_brights", "classic_reds", "deep_darks", "metallics_glitter"]
    }
    return recommendations.get(skin_tone, ["medium_brights", "classic_reds", "metallics_glitter"])

def create_color_card(color_info):
    return f"""
    <div style="margin: 10px 0; display: flex; justify-content: space-between; align-items: center; background: #fff5f7; padding: 8px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
        <a href="{color_info['link']}" target="_blank" style="color: #FF69B4; text-decoration: none; font-family: 'Arial', sans-serif; font-size: 1em;">{color_info['name']} ✨</a>
        <span style="color: #000; font-weight: bold;">{color_info['price']} 💎</span>
    </div>
    """

def main():
    st.set_page_config(page_title="💅 Elegant Nail Polish Advisor", page_icon="💅", layout="wide")
    st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #fff5f7 0%, #ffe6f0 50%, #f0e6f0 100%);
        min-height: 100vh;
        position: relative;
        overflow: hidden;
    }
    .header {
        text-align: center;
        color: #000;
        font-size: 3em;
        font-family: 'Georgia', serif;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.2);
        animation: fadeIn 2s ease-in-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    .subheader {
        text-align: center;
        color: #000;
        font-style: italic;
        font-family: 'Arial', sans-serif;
        margin-bottom: 20px;
        animation: float 3s infinite ease-in-out;
    }
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    .recommendation-section {
        background: rgba(255, 245, 247, 0.9);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        animation: pulse 4s infinite;
        position: relative;
        z-index: 1;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.01); }
        100% { transform: scale(1); }
    }
    .flower {
        position: absolute;
        font-size: 2em;
        opacity: 0.7;
        animation: floatFlower 8s infinite ease-in-out;
    }
    @keyframes floatFlower {
        0% { transform: translate(0, 0) rotate(0deg); }
        25% { transform: translate(50px, 20px) rotate(10deg); }
        50% { transform: translate(100px, 0) rotate(0deg); }
        75% { transform: translate(50px, -20px) rotate(-10deg); }
        100% { transform: translate(0, 0) rotate(0deg); }
    }
    .glitter {
        position: absolute;
        font-size: 1.2em;
        color: #FF69B4;
        opacity: 0.6;
        animation: sparkle 2s infinite;
    }
    @keyframes sparkle {
        0% { opacity: 0; transform: scale(0.5); }
        50% { opacity: 1; transform: scale(1.2); }
        100% { opacity: 0; transform: scale(0.5); }
    }
    .stApp {
        background: none;
    }
    .left-column {
        background-color: #fffaf0;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

    # Add dynamic background elements
    flower_positions = [
        {"top": "10%", "left": "10%", "emoji": "🌸"},
        {"top": "20%", "right": "15%", "emoji": "🌷"},
        {"top": "70%", "left": "20%", "emoji": "🌹"},
        {"top": "50%", "right": "10%", "emoji": "🌺"}
    ]
    glitter_positions = [
        {"top": "5%", "left": "5%"}, {"top": "15%", "right": "20%"},
        {"top": "60%", "left": "30%"}, {"top": "80%", "right": "5%"}
    ]
    background_elements = "".join([f'<div class="flower" style="top: {pos["top"]}; {"left: " + pos["left"] if "left" in pos else "right: " + pos["right"]};">{pos["emoji"]}</div>' for pos in flower_positions])
    background_elements += "".join([f'<div class="glitter" style="top: {pos["top"]}; {"left: " + pos["left"] if "left" in pos else "right: " + pos["right"]};">✨</div>' for pos in glitter_positions])
    st.markdown(f'<div style="position: fixed; width: 100%; height: 100%; z-index: 0;">{background_elements}</div>', unsafe_allow_html=True)

    st.markdown('<h1 class="header">💅 Elegant Nail Polish Advisor</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subheader">Discover your perfect shade, darling! 🌹✨</p>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<div class="left-column">', unsafe_allow_html=True)
        st.header("📸 Capture Your Elegance")
        input_method = st.radio("Choose your style:", ["📷 Camera", "📁 Upload Photo"], horizontal=True)
        
        uploaded_image = None
        if input_method == "📷 Camera":
            uploaded_image = st.camera_input("📸 Snap a chic hand photo, love! 💕")
        else:
            uploaded_image = st.file_uploader("📁 Upload a glamorous hand image", type=['png', 'jpg', 'jpeg'])
        
        if uploaded_image is not None:
            image = Image.open(uploaded_image)
            rgb_image = np.array(image)
            if len(rgb_image.shape) == 3 and rgb_image.shape[2] == 3:
                with st.spinner("🔍 Unveiling your unique glow..."):
                    avg_color, _ = extract_hand_skin_color_improved(rgb_image)
                    if avg_color is not None:
                        skin_tone = analyze_skin_tone_improved(avg_color)
                        st.success(f"✅ Your skin tone: {skin_tone.replace('_', ' ').title()} 🌟 – A perfect canvas!")
                        with col2:
                            st.markdown('<div class="recommendation-section">', unsafe_allow_html=True)
                            st.markdown("## 🎀 Your Exquisite Recommendations")
                            st.markdown('<p style="text-align: center; color: #000;">Elevate your look with these stunning shades! 💃</p>', unsafe_allow_html=True)
                            recommended_categories = get_color_recommendations(skin_tone)
                            for category_key in recommended_categories:
                                if category_key in COMPREHENSIVE_COLOR_PALETTE:
                                    for color_info in COMPREHENSIVE_COLOR_PALETTE[category_key]["colors"]:
                                        st.markdown(create_color_card(color_info), unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.error("❌ Oh no! Couldn’t detect your hand. Try better lighting or a clearer pose. 🌸")
            else:
                st.error("❌ Please upload a colorful image, dear! 🎨")
        else:
            with col2:
                st.markdown('<div class="recommendation-section">', unsafe_allow_html=True)
                st.markdown("## 🌺 Full Collection of Elegance")
                st.markdown('<p style="text-align: center; color: #000;">Explore every luxurious shade! 💄</p>', unsafe_allow_html=True)
                for category_key, category_data in COMPREHENSIVE_COLOR_PALETTE.items():
                    for color_info in category_data["colors"]:
                        st.markdown(create_color_card(color_info), unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
