
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Step 1: Locate the PDF folder
folder = Path(__file__).resolve().parent.parent / "data"

# Step 2: Load all PDF files
pages = []

for pdf in folder.glob("*.pdf"):
    loader = PyPDFLoader(str(pdf))
    pages.extend(loader.load())
    print("Loaded:", pdf.name)

if not pages:
    print("No PDF files found.")
    exit()

print("Total pages:", len(pages))

# Step 3: Split documents into chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)

chunks = splitter.split_documents(pages)

# Step 4: Display results
print("Total chunks:", len(chunks))

if chunks:
    print("\nFirst chunk:\n", chunks[0].page_content)
    print("\nSource:", Path(chunks[0].metadata["source"]).name)
    print("Page:", chunks[0].metadata["page"] + 1)
