import streamlit as st
import chromadb
from sentence_transformers import SentenceTransformer
import requests
import json
import os

st.set_page_config(page_title="आध्यात्मिक सत्य — AI सहायक", page_icon="ॐ", layout="centered")

css = '''
<style>
    .stApp { background: linear-gradient(135deg, #1a0a00 0%, #2d1500 100%); }
    h1 { color: #FFD700 !important; text-align: center; font-family: serif; }
    .subtitle { color: #FFA500; text-align: center; font-size: 14px; margin-bottom: 20px; }
    .book-answer {
        background: linear-gradient(135deg, #2d1500, #1a0a00);
        border: 1px solid #FFD700; border-radius: 10px;
        padding: 20px; color: #FFF8DC; font-family: serif;
    }
</style>
'''
st.markdown(css, unsafe_allow_html=True)

@st.cache_resource
def load_models():
    embed_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    chroma_client = chromadb.PersistentClient(path="chromadb")
    collection = chroma_client.get_collection("aadhyatmik_satya")
    return embed_model, collection

embed_model, collection = load_models()
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")

def search_book(question):
    q_embed = embed_model.encode(question).tolist()
    results = collection.query(query_embeddings=[q_embed], n_results=3)
    return [{"text": doc, "page": meta["page"]} for doc, meta in zip(results["documents"][0], results["metadatas"][0])]

st.markdown("# ॐ आधुनिक सत्य")
question = st.text_input("अपना प्रश्न पूछें...")
if st.button("उत्तर जानें") and question:
    if not GROQ_API_KEY: st.error("API Key Missing in Streamlit Secrets")
    else:
        chunks = search_book(question)
        st.markdown(f'<div class="book-answer">{chunks[0]["text"]}</div>', unsafe_allow_html=True)
