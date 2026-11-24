
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Step 1: Locate the main project folder
folder = Path(__file__).resolve().parent.parent

# Step 2: Load API key
load_dotenv(folder / ".env")

# Step 3: Set file paths
pdf_path = folder / "data" / "spotify_web_app_architecture.pdf"
index_path = folder / "faiss_index"

# Step 4: Create embedding model
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Step 5: Create FAISS index only if it doesn't exist
if (index_path / "index.faiss").exists() and (index_path / "index.pkl").exists():
    print("Existing FAISS database found!")
else:
    pages = PyPDFLoader(str(pdf_path)).load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(pages)

    db = FAISS.from_documents(chunks, embeddings)
    db.save_local(str(index_path))

    print("FAISS database created successfully!")
    print("Total chunks stored:", len(chunks))
