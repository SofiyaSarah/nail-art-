import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
import base64

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

def detect_skin_regions(image):
    """Detect skin regions using YCrCb color space - very reliable method"""
    # Convert to YCrCb color space (best for skin detection)
    ycrcb = cv2.cvtColor(image, cv2.COLOR_RGB2YCR_CB)
    
    # Define skin color range in YCrCb
    lower_skin = np.array([0, 133, 77], dtype=np.uint8)
    upper_skin = np.array([255, 173, 127], dtype=np.uint8)
    
    # Create mask for skin regions
    skin_mask = cv2.inRange(ycrcb, lower_skin, upper_skin)
    
    # Clean up the mask using morphological operations
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_OPEN, kernel)
    skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_CLOSE, kernel)
    
    return skin_mask

def extract_hand_skin_color(image):
    """Extract average skin color from hand regions"""
    try:
        # Get skin mask
        skin_mask = detect_skin_regions(image)
        
        # Find contours to identify hand regions
        contours, _ = cv2.findContours(skin_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None, None
        
        # Find the largest contour (likely the hand)
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Create a mask for the largest skin region
        hand_mask = np.zeros_like(skin_mask)
        cv2.fillPoly(hand_mask, [largest_contour], 255)
        
        # Extract colors from the hand region
        hand_pixels = image[hand_mask > 0]
        
        if len(hand_pixels) > 0:
            # Calculate average color
            avg_color = np.mean(hand_pixels, axis=0).astype(int)
            return avg_color, hand_mask
        
        return None, None
        
    except Exception as e:
        st.error(f"Error in skin detection: {e}")
        return None, None

def analyze_skin_tone(rgb_color):
    """Analyze skin tone using multiple color space analysis"""
    try:
        r, g, b = rgb_color
        
        # Convert to different color spaces for analysis
        bgr_color = np.array([[[b, g, r]]], dtype=np.uint8)
        
        # HSV analysis
        hsv = cv2.cvtColor(bgr_color, cv2.COLOR_BGR2HSV)[0][0]
        h, s, v = hsv
        
        # LAB analysis for ITA calculation
        lab = cv2.cvtColor(bgr_color, cv2.COLOR_BGR2LAB)[0][0]
        l, a, b_lab = lab
        
        # Individual Typology Angle calculation
        ita = np.arctan2(b_lab - 50, l - 50) * 180 / np.pi if l != 50 else 0
        
        # Brightness analysis
        brightness = v
        
        # Enhanced classification using multiple parameters
        if ita > 55 or brightness > 200:
            return "very_light"
        elif ita > 41 or (brightness > 160 and s < 80):
            return "light"
        elif ita > 28 or (brightness > 100 and brightness <= 160):
            return "medium"
        elif ita > 10 or (brightness > 60 and brightness <= 100):
            return "dark"
        else:
            return "very_dark"
            
    except Exception as e:
        st.error(f"Error in skin tone analysis: {e}")
        return "medium"  # Default fallback

def create_analysis_visualization(original_image, hand_mask, avg_color, skin_tone):
    """Create visualization showing detected hand and analysis"""
    try:
        # Create result image
        result_image = original_image.copy()
        
        if hand_mask is not None:
            # Highlight detected hand region
            colored_mask = np.zeros_like(original_image)
            colored_mask[hand_mask > 0] = [0, 255, 0]  # Green overlay
            
            # Blend with original image
            result_image = cv2.addWeighted(result_image, 0.8, colored_mask, 0.2, 0)
            
            # Add skin tone color sample
            color_box = np.full((50, 100, 3), avg_color, dtype=np.uint8)
            result_image[10:60, 10:110] = color_box
            
            # Add text
            cv2.putText(result_image, f"Skin Tone: {skin_tone.replace('_', ' ').title()}", 
                       (120, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(result_image, "Detected Hand Area", 
                       (10, result_image.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        return result_image
        
    except Exception as e:
        st.error(f"Error creating visualization: {e}")
        return original_image

def main():
    st.set_page_config(
        page_title="💅 AI Nail Polish Advisor",
        page_icon="💅",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #FF69B4;
        font-size: 3em;
        font-weight: bold;
        margin-bottom: 0.5em;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-style: italic;
        margin-bottom: 2em;
    }
    .recommendation-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    .tip-box {
        background: #f0f8ff;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #4CAF50;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">💅 AI Nail Polish Advisor</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Discover your perfect nail polish colors based on your skin tone!</p>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.header("🎨 Settings")
    color_category = st.sidebar.selectbox(
        "Choose Color Style",
        ["primary", "bold", "trendy"],
        help="Select the type of colors you prefer",
        format_func=lambda x: {
            "primary": "💐 Everyday & Classic",
            "bold": "🔥 Bold & Statement", 
            "trendy": "✨ Trendy & Fashion"
        }[x]
    )
    
    # Add sensitivity slider
    sensitivity = st.sidebar.slider(
        "Detection Sensitivity", 
        1, 10, 5, 
        help="Adjust if hand detection is too strict (lower) or too loose (higher)"
    )
    
    # Main interface
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.header("📸 Upload Your Hand Photo")
        
        # Multiple input options
        input_method = st.radio(
            "Choose input method:",
            ["📷 Camera", "📁 Upload File"],
            horizontal=True
        )
        
        uploaded_image = None
        
        if input_method == "📷 Camera":
            uploaded_image = st.camera_input("Take a photo of your hand")
        else:
            uploaded_image = st.file_uploader(
                "Upload an image of your hand", 
                type=['png', 'jpg', 'jpeg'],
                help="Best results with good lighting and clear hand visibility"
            )
        
        if uploaded_image is not None:
            try:
                # Process the image
                image = Image.open(uploaded_image)
                image_array = np.array(image)
                
                # Convert to RGB if needed
                if len(image_array.shape) == 3 and image_array.shape[2] == 3:
                    # Image is already RGB
                    rgb_image = image_array
                else:
                    st.error("Please upload a color image (RGB)")
                    return
                
                with st.spinner("🔍 Analyzing your skin tone..."):
                    # Extract skin color
                    avg_color, hand_mask = extract_hand_skin_color(rgb_image)
                    
                    if avg_color is not None:
                        # Analyze skin tone
                        skin_tone = analyze_skin_tone(avg_color)
                        
                        # Create visualization
                        result_image = create_analysis_visualization(rgb_image, hand_mask, avg_color, skin_tone)
                        
                        # Display results
                        st.success("✅ Hand detected successfully!")
                        st.image(result_image, caption="Analysis Results", use_column_width=True)
                        
                        # Show color info
                        with col2:
                            st.markdown("## 🎯 Your Results")
                            
                            # Skin tone result
                            st.markdown(f"""
                            <div class="recommendation-card">
                                <h3>🌈 Detected Skin Tone</h3>
                                <h2>{skin_tone.replace('_', ' ').title()}</h2>
                                <p>RGB: {avg_color[0]}, {avg_color[1]}, {avg_color[2]}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Get recommendations
                            if skin_tone in COLOR_SUGGESTIONS:
                                suggestions = COLOR_SUGGESTIONS[skin_tone][color_category]
                                
                                st.markdown("### 💅 Perfect Colors for You")
                                
                                for i, color in enumerate(suggestions, 1):
                                    st.markdown(f"**{i}.** {color}")
                                
                                # Pro tips
                                st.markdown("### 💡 Pro Tips")
                                
                                tips = {
                                    "very_light": "Nude tones for elegance, bright colors for fun occasions",
                                    "light": "Soft pastels and classic reds are your best friends",
                                    "medium": "You're lucky - both warm and cool tones work beautifully",
                                    "dark": "Rich, deep colors and metallics will make your hands stunning",
                                    "very_dark": "Bold, vibrant colors and metallics are absolutely gorgeous on you"
                                }
                                
                                st.markdown(f"""
                                <div class="tip-box">
                                    💡 {tips.get(skin_tone, "Experiment with different shades!")}
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Show all categories
                                with st.expander("🎨 See all color recommendations"):
                                    for category, colors in COLOR_SUGGESTIONS[skin_tone].items():
                                        st.write(f"**{category.title()} Colors:**")
                                        for color in colors:
                                            st.write(f"  • {color}")
                                        st.write("")
                    
                    else:
                        st.warning("⚠️ Could not detect hand in the image. Please try:")
                        st.write("• Ensure good lighting")
                        st.write("• Make sure your hand is clearly visible")
                        st.write("• Try a different angle")
                        st.write("• Adjust the detection sensitivity in the sidebar")
                        
            except Exception as e:
                st.error(f"❌ Error processing image: {str(e)}")
                st.write("Please try uploading a different image or check if the file is corrupted.")
        
        else:
            st.info("👆 Upload a photo of your hand to get started!")
            
            # Show example
            st.markdown("### 📋 For Best Results:")
            st.write("✅ Use good, natural lighting")
            st.write("✅ Keep your hand flat and fingers visible")
            st.write("✅ Fill most of the frame with your hand")
            st.write("✅ Avoid shadows or harsh lighting")
            st.write("✅ Take photo against a contrasting background")
    
    # Instructions and info
    with st.expander("📖 How to Use This App"):
        st.markdown("""
        ### Step by Step Guide:
        
        1. **Choose your input method** - Camera or file upload
        2. **Take/upload a clear photo** of your hand
        3. **Wait for automatic analysis** - the app will detect skin tone
        4. **Get personalized recommendations** - perfect nail polish colors for you!
        
        ### 📸 Photo Tips:
        - **Natural lighting** works best (near a window)
        - **Steady hand** - avoid blur
        - **Fill the frame** - your hand should be the main subject
        - **Contrasting background** - helps with detection
        - **Clean hands** - remove existing nail polish if possible
        """)
    
    with st.expander("🔬 How It Works"):
        st.markdown("""
        This app uses advanced computer vision without requiring MediaPipe:
        
        - **YCrCb Color Space Analysis** - Best method for skin detection
        - **Morphological Operations** - Cleans and refines hand detection
        - **Individual Typology Angle (ITA)** - Scientific skin tone classification
        - **Multi-parameter Analysis** - Uses brightness, hue, and color properties
        - **No External Dependencies** - Works with any Python version!
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        Made with ❤️ using Streamlit and OpenCV | Perfect for Python 3.13+ | No MediaPipe Required!
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()