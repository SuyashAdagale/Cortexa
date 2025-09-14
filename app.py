import os
import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import base64
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

st.set_page_config(
    page_title="Cortexa",
    page_icon="🤖",
    layout="wide"
)

st.sidebar.title("⚙️ Settings")
model_choice = st.sidebar.selectbox(
    "Choose AI Model",
    ["Gemini", "Groq", "Claude"]
)
theme = st.sidebar.radio("Theme", ["🌞 Light", "🌙 Dark"])
language = st.sidebar.selectbox("Language", ["English", "हिन्दी", "मराठी"])

mode = st.sidebar.radio(
    "Select Mode",
    ["💬 Chat", "🎨 Image Generation", "📷 Image Q&A"]
)
st.sidebar.markdown("---")
st.sidebar.info("This is a multi-model AI chatbot built by Suyash.")

st.title("🤖 Cortex")

if mode == "💬 Chat":
    st.subheader(f"Chatting with {model_choice}")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("What would you like to ask?")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response_container = st.empty()
            response = ""

            try:
                if model_choice == "Gemini":
                    genai.configure(api_key=GEMINI_API_KEY)
                    model = genai.GenerativeModel("gemini-2.5-flash")
                    response_obj = model.generate_content(prompt)
                    response = response_obj.text

                elif model_choice == "Groq":
                    from groq import Groq
                    client = Groq(api_key=GROQ_API_KEY)
                    response_obj = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    response = response_obj.choices[0].message.content


                elif model_choice == "Claude":
                    from anthropic import Anthropic  # type: ignore i will implement it afterwards
                    client = Anthropic(api_key=CLAUDE_API_KEY)  # type: ignore sir it is paid
                    response_obj = client.messages.create(
                        model="claude-3-haiku-20240307",
                        max_tokens=1024,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    response = response_obj.content[0].text

                response_container.markdown(response)

            except Exception as e:
                st.error(f"An error occurred: {e}")
                response = f"Sorry, I encountered an error with the {model_choice} API."
                response_container.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})

elif mode == "🎨 Image Generation":
    st.subheader("Generate Images with Gemini 2.5")

    img_prompt = st.text_input("Enter your image prompt:")

    if st.button("Generate Image") and img_prompt:
        with st.spinner("Generating your masterpiece... ✨"):
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                model = genai.GenerativeModel("gemini-2.5-flash-image-preview")
                response = model.generate_content([img_prompt])

                for part in response.candidates[0].content.parts:
                    if part.inline_data:
                        image_data = part.inline_data.data
                        image_bytes = base64.b64decode(image_data)
                        img = Image.open(io.BytesIO(image_bytes))
                        st.image(img, caption=f"Generated Image: {img_prompt}", use_container_width=True)

            except Exception as e:
                st.error(f"Image generation failed: {e}")

elif mode == "📷 Image Q&A":
    st.subheader("Upload an Image and Ask Questions (Coming Soon 🚧)")
    st.info("This feature is under construction. Soon you'll be able to get insights about your images!")
