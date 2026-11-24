
from pathlib import Path
import os
import json
import re

from dotenv import load_dotenv
from neo4j import GraphDatabase
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI

# Step 1: Load project settings
folder = Path(__file__).resolve().parent.parent
load_dotenv(folder / ".env")

pdf_folder = folder / "data"
cache_folder = folder / "graph_cache"
cache_folder.mkdir(exist_ok=True)

# Step 2: Load PDFs and split into chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    model_kwargs={"response_format": {"type": "json_object"}}
)

relationships = []

for pdf in pdf_folder.glob("*.pdf"):
    print("Loaded:", pdf.name)

    # Reuse extraction when the PDF has not changed
    import hashlib
    pdf_hash = hashlib.sha256(pdf.read_bytes()).hexdigest()
    cache_file = cache_folder / f"{pdf.stem}_{pdf_hash[:12]}.json"

    if cache_file.exists():
        print("Using cached relationships:", pdf.name)
        data = json.loads(cache_file.read_text(encoding="utf-8"))

    else:
        pages = PyPDFLoader(str(pdf)).load()
        chunks = splitter.split_documents(pages)
        print("Total PDF chunks:", len(chunks))

        data = []

        for chunk in chunks:
            prompt = f"""
            Extract factual technology, service, and component
            relationships explicitly stated in the text.

            Return ONLY a JSON object with a "relationships" array.
            Each relationship must have:
            "source", "relation", "target".

            Example:
            {{
              "relationships": [
                {{
                  "source": "Redis",
                  "relation": "CACHES",
                  "target": "Sessions"
                }}
              ]
            }}

            Do not invent relationships.
            If none exist, return {{"relationships": []}}.

            Text:
            {chunk.page_content}
            """

            try:
                response = llm.invoke(prompt)
                result = json.loads(response.content)
                items = result.get("relationships", [])

                if isinstance(items, list):
                    for item in items:
                        if isinstance(item, dict) and all(
                            isinstance(item.get(k), str)
                            for k in ("source", "relation", "target")
                        ):
                            data.append(item)

            except (json.JSONDecodeError, TypeError, AttributeError):
                print("Skipped an invalid AI response.")

        cache_file.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        print("Extraction saved to cache.")

    relationships.extend(data)

if not relationships:
    print("No relationships found. Nothing to save.")
    raise SystemExit

# Step 3: Normalize and remove duplicates
unique = set()

for item in relationships:
    source = item["source"].strip().lower()
    target = item["target"].strip().lower()

    relation = re.sub(
        r"[^A-Z0-9_]",
        "_",
        item["relation"].strip().upper().replace(" ", "_")
    )
    relation = re.sub(r"_+", "_", relation).strip("_")

    if source and target and relation:
        unique.add((source, relation, target))

print("\nUnique relationships:", len(unique))

for source, relation, target in sorted(unique):
    print(f"{source} --[{relation}]--> {target}")

# Step 4: Connect to Neo4j
driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(
        os.getenv("NEO4J_USERNAME"),
        os.getenv("NEO4J_PASSWORD")
    )
)

# Step 5: Save automatically extracted graph
with driver.session() as session:
    for source, relation, target in unique:
        session.run("""
            MERGE (a:AutoEntity {
                project: $project,
                name: $source
            })
            MERGE (b:AutoEntity {
                project: $project,
                name: $target
            })
            MERGE (a)-[r:RELATED_TO {
                type: $relation
            }]->(b)
        """,
        project="Spotify_Hybrid_RAG",
        source=source,
        target=target,
        relation=relation
        ).consume()

driver.close()

print("\nAutomatic Knowledge Graph saved to Neo4j!")
print("Relationships processed:", len(unique))
