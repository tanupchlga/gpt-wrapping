import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Page Configuration & UI setup
st.set_page_config(page_title="Thrift Scout AI", page_icon="🕵️‍♂️", layout="centered")

st.title("🕵️‍♂️ Thrift Scout AI")
st.subheader("Instantly check if an item is vintage, authentic, and worth the price.")

# 2. Configure Gemini API Key securely from secrets
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("API Key not found! Please set GEMINI_API_KEY in your Streamlit secrets.")
    st.stop()

# 3. System prompt to give the model expert thrifting knowledge
SYSTEM_INSTRUCTION = """
You are "Thrift Scout," a cynical, highly knowledgeable antique appraiser and vintage-fashion expert.
Your goal is to help thrift store hunters evaluate items on the spot.

Based on the image or text description provided, structure your analysis EXACTLY like this:

### 🕵️‍♂️ VINTAGE CHECKLIST
- Give the user 3 specific physical clues to look for based on this item type (e.g., stitch patterns, tags, zipper brands like Talon/Conmar, wood joinery, marks/stamps).
- Give an estimated era/decade based on the visual indicators.

### 💰 VALUATION GUIDE
- Tell the user *exactly* what keywords to search on eBay "Sold" listings (not active listings) to get an accurate price.
- Highlight any hidden features that make this specific style more or less valuable.

### 🚦 THE BUY VERDICT
- Under what price is this a "Must Buy"?
- At what price is it a "Pass/Overpriced"?
- Rate the demand/collectibility from 1 to 10.
"""

# 4. User Inputs (Image Upload / Camera Capture OR Text Description)
st.write("---")
st.markdown("### 📸 Step 1: Show/Describe the Item")

# Toggle input method
input_mode = st.radio("Choose input method:", ["Camera / Image Upload", "Text Description Only"])

uploaded_image = None
description = ""

if input_mode == "Camera / Image Upload":
    # Upload photo or take live picture
    uploaded_file = st.file_uploader("Upload a photo or tag closeup:", type=["jpg", "jpeg", "png"])
    camera_file = st.camera_input("Or take a live photo:")
    
    # Prioritize camera over upload
    active_file = camera_file if camera_file is not None else uploaded_file
    
    if active_file is not None:
        uploaded_image = Image.open(active_file)
        st.image(uploaded_image, caption="Item to Appraise", width=300)

    description = st.text_input("Any extra details? (e.g., 'Asking price is $15, tag says Made in USA')")

else:
    description = st.text_area(
        "Describe the item in detail:",
        placeholder="Example: Heavy wool plaid jacket, brand is Pendleton, black and gold label, metal Talon zipper, asking price $25..."
    )

# 5. Appraise Execution
if st.button("🔍 Appraise Item"):
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=SYSTEM_INSTRUCTION
    )
    
    with st.spinner("Analyzing tags, materials, and value... Please hold."):
        try:
            if uploaded_image:
                prompt_content = [description if description else "Analyze this item for vintage status and value.", uploaded_image]
                response = model.generate_content(prompt_content)
            else:
                if not description.strip():
                    st.warning("Please provide a description or an image first!")
                    st.stop()
                response = model.generate_content(description)
                
            st.success("Analysis Complete!")
            st.write(response.text)
            
        except Exception as e:
            st.error(f"Error during appraisal: {e}")
