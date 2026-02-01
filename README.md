# Smart Document Q&A Assistant

A modular Retrieval-Augmented Generation (RAG) system that enables users to interact with PDF documents through natural language. The application manages the end-to-end pipeline: from text extraction and cleaning to vector embedding generation and semantic search.

## Technical Architecture

The system follows a standard RAG workflow to ensure accuracy and contextual relevance in responses:

1. **Ingestion**: PDFs are parsed using `pdfplumber` and cleaned of noise (page numbers, headers, etc.).
2. **Chunking**: Text is split into overlapping segments to maintain context.
3. **Embeddings**: Chunks are transformed into 384-dimensional vectors using the `all-MiniLM-L6-v2` transformer model.
4. **Vector Storage**: Vectors are stored in a FAISS index for high-speed similarity search.
5. **Persistence**: FAISS indices and text chunks are synced to Amazon S3 for long-term storage and cross-session retrieval.
6. **Generation**: Top-K relevant chunks are retrieved and passed to a Llama-3 model via Groq to generate a grounded response.

## Project Structure

```text
├── app.py              # Streamlit UI and application orchestration
├── core/
│   ├── __init__.py     # Package initialization
│   ├── processor.py    # PDF extraction and text preprocessing
│   ├── vector_store.py # FAISS index management and search logic
│   └── chat_engine.py  # RAG prompt construction and memory handling
├── utils/
│   ├── __init__.py     # Package initialization
│   └── s3_utils.py     # AWS S3 upload/download operations
├── requirements.txt    # Project dependencies
└── .gitignore          # Version control exclusions


Installation
Clone the repository:

Bash
git clone [https://github.com/SagarpatilSP/Smart-Document-Q-A-Assistant-Powered-by-RAG.git](https://github.com/SagarpatilSP/Smart-Document-Q-A-Assistant-Powered-by-RAG.git)
cd Smart-Document-Q-A-Assistant-Powered-by-RAG
Install dependencies:

Bash
pip install -r requirements.txt
Configure AWS CLI: Ensure your local machine is authenticated to access your S3 bucket.

Bash
aws configure
Enter your Access Key ID, Secret Access Key, and Region (us-east-1) when prompted.

Setup and Usage
Groq API Key
To use the LLM features, you must provide a valid Groq API Key. This key is entered directly into the application sidebar at runtime to ensure security.

Running the App
Execute the following command to launch the Streamlit server:

Bash
streamlit run app.py
Workflow
Upload: Drag and drop a PDF into the sidebar.

Process: Click to generate the index; the system will automatically upload the processed files to your S3 bucket.

Retrieve: For previously processed books, select the book name from the sidebar and click "Load" to fetch the index from S3.

Chat: Enter your queries in the chat input. The assistant uses conversational memory to answer follow-up questions.

Requirements
Python 3.9+

AWS S3 Bucket (configured in utils/s3_utils.py)

Groq Cloud Account
