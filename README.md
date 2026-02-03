🍳 Kitchen AI: Image-to-Recipe Generator
StreamlitPythonLangChain

Turn your leftovers into gourmet meals! 🥗Upload a photo of your ingredients, or type them out, and let AI generate a delicious recipe for you.

🌟 Features
📸 Image Recognition: Uses Imagga API to identify ingredients from photos.
🧠 AI Recipe Generation: Powered by Groq (Llama 3.3) for instant, creative recipes.
⚡ Lightning Fast: Delivers recipes in seconds, not minutes.
🎛️ User-Friendly: Simple, responsive interface built with Streamlit.
🚀 Tech Stack
Frontend Framework: Streamlit
Vision API: Imagga (Automated Image Tagging)
LLM Inference: Groq (Llama 3.3-70b-versatile)
Orchestration: LangChain
🛠️ Installation & Setup
1. Clone the Repository
git clone https://github.com/your-username/kitchen-ai.gitcd kitchen-ai
2. Install Dependencies
Ensure you have Python 3.8+ installed, then install the required libraries:

bash

pip install -r requirements.txt
3. Get Your API Keys
This app requires free API keys to run. Sign up for the following:

Service
Purpose
Link
Imagga	Image Recognition	Get Key
Groq	Recipe Generation	Get Key

4. Run the App
bash

streamlit run app.py
The app will open in your browser at http://localhost:8501. Paste your API keys into the sidebar to start cooking!

📸 How to Use
Text Mode: Simply type your ingredients (e.g., "Tomato, Basil, Mozzarella") and click Generate.
Image Mode:
Upload a photo of your fridge or ingredients.
The AI identifies what's in the image (e.g., "Eggs, Onion, Pepper").
The AI instantly creates a recipe based on those ingredients.
