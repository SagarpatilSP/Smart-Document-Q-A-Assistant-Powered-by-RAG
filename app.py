import streamlit as st
import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from groq import Groq
import faiss

# Import the modular functions from your new files
from core.processor import pdf_to_text, clean_text, chunk_text
from core.vector_store import create_faiss_index, retrieve_faiss
from core.chat_engine import build_context, build_memory_context, build_prompt
from utils.s3_utils import upload_to_s3, download_from_s3, s3_exists

# ----------------------------
# ✅ CONFIGURATION
# ----------------------------
st.set_page_config(page_title="📘 Book Chatbot (RAG + Memory)", page_icon="📘", layout="wide")

OUTPUT_FOLDER = "processed_output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

FAISS_INDEX_PATH = os.path.join(OUTPUT_FOLDER, "book_index.faiss")
CHUNKS_PATH = os.path.join(OUTPUT_FOLDER, "book_chunks.json")
S3_PREFIX = "book-chatbot"

# ----------------------------
# ✅ SESSION STATE INITIALIZATION
# ----------------------------
if "embed_model" not in st.session_state:
    st.session_state.embed_model = SentenceTransformer("all-MiniLM-L6-v2")

if "index" not in st.session_state:
    st.session_state.index = None

if "chunks" not in st.session_state:
    st.session_state.chunks = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ----------------------------
# ✅ SIDEBAR & SETTINGS
# ----------------------------
st.sidebar.header("⚙️ Settings")

# S3 Book Selection Logic
def get_available_books():
    import boto3
    s3 = boto3.client("s3")
    from utils.s3_utils import S3_BUCKET
    resp = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=f"{S3_PREFIX}/faiss/", Delimiter="/")
    return [p["Prefix"].split("/")[-2] for p in resp.get("CommonPrefixes", [])]

available_books = get_available_books()
selected_book = st.sidebar.selectbox("Choose an indexed book", available_books) if available_books else None

k = st.sidebar.slider("Top-K Retrieved Chunks", 1, 10, 5)
max_context_chars = st.sidebar.slider("Max Context Size", 1000, 12000, 4000, 500)

groq_api_key = st.sidebar.text_input("Enter Groq API Key", type="password")
if groq_api_key:
    st.session_state.groq_client = Groq(api_key=groq_api_key)

# ----------------------------
# ✅ MAIN UI - STEP 1: UPLOAD & PROCESS
# ----------------------------
st.title("📘 Book Chatbot (RAG + Conversational Memory)")
st.subheader("📂 Step 1: Upload PDF and Process")

uploaded_pdf = st.file_uploader("Upload PDF Book", type=["pdf"])

if uploaded_pdf:
    book_name = os.path.splitext(uploaded_pdf.name)[0]
    if st.button("🚀 Extract + Clean + Chunk"):
        with st.spinner("Processing..."):
            raw = pdf_to_text(uploaded_pdf)
            cleaned = clean_text(raw)
            st.session_state.chunks = chunk_text(cleaned)
            st.success(f"✅ Created {len(st.session_state.chunks)} chunks!")

# ----------------------------
# ✅ STEP 2: INDEXING
# ----------------------------
st.subheader("🧠 Step 2: Create FAISS Index")
if st.session_state.chunks:
    if st.button("⚡ Build & Save Index to S3"):
        with st.spinner("Building index..."):
            embeds = st.session_state.embed_model.encode(st.session_state.chunks).astype("float32")
            st.session_state.index = create_faiss_index(embeds)
            
            # Save local copies
            faiss.write_index(st.session_state.index, FAISS_INDEX_PATH)
            with open(CHUNKS_PATH, "w") as f:
                json.dump(st.session_state.chunks, f)
            
            # Upload to S3
            upload_to_s3(FAISS_INDEX_PATH, f"{S3_PREFIX}/faiss/{book_name}/index.faiss")
            upload_to_s3(CHUNKS_PATH, f"{S3_PREFIX}/faiss/{book_name}/chunks.json")
            st.success("✅ Index synced to S3!")

# ----------------------------
# ✅ STEP 3: CHAT
# ----------------------------
st.subheader("💬 Step 3: Chat with Book")

# Load existing index if selected
if selected_book and st.session_state.index is None:
    if st.button(f"Load {selected_book}"):
        download_from_s3(FAISS_INDEX_PATH, f"{S3_PREFIX}/faiss/{selected_book}/index.faiss")
        download_from_s3(CHUNKS_PATH, f"{S3_PREFIX}/faiss/{selected_book}/chunks.json")
        st.session_state.index = faiss.read_index(FAISS_INDEX_PATH)
        st.session_state.chunks = json.load(open(CHUNKS_PATH))
        st.rerun()

# Chat interface
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_query = st.chat_input("Ask a question about the book...")

if user_query:
    if not st.session_state.index:
        st.error("Please load or create an index first.")
    elif "groq_client" not in st.session_state:
        st.error("Please enter your Groq API Key.")
    else:
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):
            results = retrieve_faiss(user_query, st.session_state.index, st.session_state.chunks, st.session_state.embed_model, k=k)
            context = build_context(results, max_chars=max_context_chars)
            memory = build_memory_context(st.session_state.chat_history)
            prompt = build_prompt(context, user_query, memory)
            
            completion = st.session_state.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            answer = completion.choices[0].message.content
            st.markdown(answer)
            st.session_state.chat_history.append({"role": "assistant", "content": answer})