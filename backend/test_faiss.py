
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

# Step 1: Locate main project folder
folder = Path(__file__).resolve().parent.parent

# Step 2: Load API key
load_dotenv(folder / ".env")

# Step 3: Locate existing FAISS index
index_path = folder / "faiss_index"

# Step 4: Load embeddings and FAISS database
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

db = FAISS.load_local(
    str(index_path),
    embeddings,
    allow_dangerous_deserialization=True
)

# Step 5: Search the database
question = "Which databases are used in the Spotify architecture?"

results = db.similarity_search(question, k=3)

# Step 6: Display results
for i, doc in enumerate(results, start=1):
    print(f"\nResult {i} - Page {doc.metadata['page'] + 1}")
    print(doc.page_content)
