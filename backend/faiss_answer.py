
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

# Step 1: Locate project folder and load API key
folder = Path(__file__).resolve().parent.parent
load_dotenv(folder / ".env")

# Step 2: Load existing FAISS database
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

db = FAISS.load_local(
    str(folder / "faiss_index"),
    embeddings,
    allow_dangerous_deserialization=True
)

# Step 3: Ask a question
question = "What technologies are used in Spotify frontend?"

# Step 4: Retrieve relevant PDF chunks
documents = db.similarity_search(question, k=3)
context = "\n\n".join(doc.page_content for doc in documents)

# Step 5: Generate answer using OpenAI
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

prompt = f"""
Answer using only the PDF context below.
If the answer is unavailable, say "Information not found in PDF".

Context:
{context}

Question:
{question}
"""

response = llm.invoke(prompt)

print("\nFAISS RAG ANSWER:\n")
print(response.content)
