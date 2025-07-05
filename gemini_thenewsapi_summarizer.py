import streamlit as st
import requests
import google.generativeai as genai
from dotenv import load_dotenv
import os

# ---- Load API Keys from .env ----
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
THENEWSAPI_KEY = os.getenv("THENEWSAPI_KEY")

# ---- Configure Gemini ----
genai.configure(api_key=GEMINI_API_KEY)

# ---- Load Gemini Flash Model ----
try:
    model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
except Exception as e:
    model = None
    model_error = str(e)

# ---- Fetch News from TheNewsAPI ----
def fetch_news():
    url = f"https://api.thenewsapi.com/v1/news/top?api_token={THENEWSAPI_KEY}&language=en&country=in"
    response = requests.get(url)
    return response.json().get("data", [])[:5]

# ---- Summarize with Gemini ----
def summarize_article(content):
    prompt = f"""Summarize the following news article in brief and detail about 4 lines even if content is short:\n\n{content}\n\nSummary:"""
    response = model.generate_content(prompt)
    return response.text.strip()

# ---- Streamlit UI ----
st.set_page_config(page_title="Gemini News Summarizer", page_icon="📰")
st.title("📰 News Summarizer using AI")
st.write("Summarizes top Indian news using Google Gemini 1.5 Flash and TheNewsAPI")

if model is None:
    st.error(f"Gemini model could not be initialized:\n{model_error}")
else:
    if st.button("Fetch & Summarize News"):
        articles = fetch_news()
        for article in articles:
            st.subheader(article.get("title", "No Title"))
            st.write(f"**Source:** {article.get('source', 'Unknown')}")
            st.markdown(f"[🔗 Read Full Article]({article.get('url', '#')})", unsafe_allow_html=True)
            full_text = article.get("content") or article.get("description") or article.get("title", "")
            if not full_text or len(full_text.strip()) < 30:
                st.info("ℹ️ Not enough content to summarize. Here's a short preview:")
                st.write(full_text)
                continue
            with st.spinner("Summarizing..."):
                try:
                    summary = summarize_article(full_text)
                    st.success("Summary:")
                    st.write(summary)
                except Exception as e:
                    st.error(f"❌ Error during summarization: {e}")
