import streamlit as st
import base64
import requests
from io import BytesIO
from PIL import Image

# --- IMPORTS ---
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# --- CONFIGURATION ---
st.set_page_config(page_title="Kitchen AI (Imagga + Llama 3.3)", layout="wide")

with st.sidebar:
    st.header("🔑 Configuration")
    
    st.markdown("### Vision Provider (Imagga)")
    st.info("Using **Imagga** (Tagging API)")
    imagga_key = st.text_input("Imagga API Key", type="password", help="Get it at imagga.com/dashboard")
    imagga_secret = st.text_input("Imagga API Secret", type="password", help="Get it at imagga.com/dashboard")
    
    st.markdown("---")
    st.markdown("### Recipe Provider (Groq)")
    st.info("Using **Llama 3.3** (Latest)")
    groq_key = st.text_input("Groq API Key", type="password", help="Get it at console.groq.com")
    
    # --- NEW: Recipe Model Selector ---
    with st.expander("⚙️ Recipe Model Settings"):
        recipe_models = [
            "llama-3.3-70b-versatile", # NEW Replacement (Recommended)
            "llama-3.1-8b-instant",   # Faster/Smaller Backup
            "gemma2-9b-it"            # Alternative
        ]
        selected_recipe_model = st.selectbox(
            "Select Recipe Model:",
            options=recipe_models,
            index=0,
            help="Llama 3.3 is the new replacement for 3.1 70b."
        )

if not imagga_key or not imagga_secret or not groq_key:
    st.warning("⚠️ Please enter Imagga Key, Secret, AND Groq Key.")
    st.stop()

# --- FIX: Strip whitespace from keys ---
imagga_key = imagga_key.strip()
imagga_secret = imagga_secret.strip()
groq_key = groq_key.strip()

# --- KNOWLEDGE BASE ---
COOKBOOK_CONTEXT = """
1. Shakshuka: Eggs poached in a sauce of tomatoes, olive oil, peppers, onion, and garlic. Commonly spiced with cumin, paprika, and cayenne.
2. Caprese Salad: Simple Italian salad made of sliced fresh mozzarella, tomatoes, and sweet basil. Seasoned with salt and olive oil.
3. Chicken Curry: Dish made with chicken, onion, tomato, ginger, garlic, and spices like turmeric, cumin, and coriander. Often served with rice or roti.
4. Fried Rice: Made with cooked rice, soy sauce, egg, vegetables like carrots and peas, and meat like chicken or shrimp. Cooked in a wok.
5. Omelette: Beat eggs, salt, pepper. Melt butter in pan. Pour eggs, let set. Add cheese, ham, or vegetables. Fold and serve.
6. Avocado Toast: Toast bread. Mash avocado with lemon and salt. Spread on bread. Top with chili flakes or tomato.
"""

# --- FUNCTIONS ---

def analyze_image_imagga(image_bytes):
    """
    Uses Imagga API to detect tags/ingredients in the image.
    """
    try:
        # --- STEP 1: Convert Image to Base64 ---
        img = Image.open(BytesIO(image_bytes))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        img_bytes_jpeg = buffered.getvalue()
        img_base64 = base64.b64encode(img_bytes_jpeg).decode('utf-8')
        
        # --- STEP 2: Call Imagga API ---
        api_url = "https://api.imagga.com/v2/tags"
        
        payload = {
            "image_base64": img_base64,
            "language": "en",
            "limit": 10
        }
        
        response = requests.post(
            api_url, 
            auth=(imagga_key, imagga_secret), 
            data=payload
        )
        
        if response.status_code != 200:
            st.error(f"Imagga API Error {response.status_code}: {response.text}")
            return "None"
            
        result = response.json()
        
        # --- STEP 3: Parse Tags ---
        if "result" in result and "tags" in result["result"]:
            tags_list = [tag["tag"]["en"] for tag in result["result"]["tags"]]
            description = ", ".join(tags_list)
            return description
        else:
            st.error("No tags found in image.")
            return "None"
            
    except Exception as e:
        st.error(f"Imagga Error: {e}")
        return "None"

def generate_recipe_groq(description, model_name):
    """Uses Groq Llama for Text Generation (Dynamic Model)."""
    try:
        llm = ChatGroq(model=model_name, api_key=groq_key, temperature=0.7)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful chef. Use the following recipes from your knowledge base to inspire your answer. If the user's description contains ingredients, extract them. If user's ingredients don't match a recipe perfectly, use general knowledge but follow the style of the base recipes.\n\nKnowledge Base:\n{context}"),
            ("human", "Here is a description/ingredients: '{description}'. \n\nSuggest a detailed recipe.")
        ])
        
        chain = (
            prompt 
            | llm 
            | StrOutputParser()
        )
        
        return chain.invoke({
            "context": COOKBOOK_CONTEXT,
            "description": description
        })
    except Exception as e:
        st.error(f"Groq Error: {e}")
        raise e

# --- UI ---

st.title("🔍 Kitchen AI (Imagga + Llama 3.3)")
st.markdown(f"**Vision:** Imagga | **Recipe:** {selected_recipe_model}")

final_description = ""

tab1, tab2 = st.tabs(["📝 Text", "📸 Image"])

with tab1:
    user_input = st.text_area("Enter your ingredients (e.g., tomato, eggs, basil):", height=120)
    if st.button("Generate Recipe (Text)", key="btn_text"):
        final_description = user_input

with tab2:
    uploaded_file = st.file_uploader("Upload a photo of your ingredients", type=["jpg", "png", "jpeg", "webp"])
    
    col_a, col_b = st.columns([1, 2])
    
    if uploaded_file:
        with col_a:
            st.image(uploaded_file, caption="Preview", width=300)
        
        with col_b:
            if st.button("Analyze Image & Generate", key="btn_img"):
                with st.spinner("👀 Imagga is tagging ingredients..."):
                    img_bytes = uploaded_file.getvalue()
                    
                    description = analyze_image_imagga(img_bytes)
                    
                    st.info(f"👀 Identified Ingredients: {description}")
                    
                    if description == "None" or "Error" in str(description):
                        st.error("❌ AI failed to process image.")
                    else:
                        final_description = description

if final_description:
    st.divider()
    st.subheader("🧑‍🍳 Chef's Recommendation")
    
    with st.spinner(f"{selected_recipe_model} is cooking the recipe..."):
        try:
            recipe = generate_recipe_groq(final_description, selected_recipe_model)
            st.markdown(recipe)
        except Exception as e:
            st.error(f"Error: {e}")