
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from neo4j import GraphDatabase
from concurrent.futures import ThreadPoolExecutor
import os
import re

# Step 1: Load credentials
folder = Path(__file__).resolve().parent.parent
load_dotenv(folder / ".env")

question = input("Enter your question: ").strip()

# Step 2: Search FAISS
def search_faiss():
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    db = FAISS.load_local(
        str(folder / "faiss_index"),
        embeddings,
        allow_dangerous_deserialization=True
    )

    docs = db.similarity_search(question, k=4)
    return "\n\n".join(doc.page_content for doc in docs)


# Step 3: Search Neo4j
def search_graph():
    driver = GraphDatabase.driver(
        os.getenv("NEO4J_URI"),
        auth=(
            os.getenv("NEO4J_USERNAME"),
            os.getenv("NEO4J_PASSWORD")
        )
    )

    try:
        with driver.session() as session:
            records = session.run("""
                MATCH (a:AutoEntity {project: $project})
                      -[r:RELATED_TO]->
                      (b:AutoEntity {project: $project})
                RETURN a.name AS source,
                       r.type AS relation,
                       b.name AS target
            """, project="Spotify_Hybrid_RAG")

            relationships = [
                (r["source"], r["relation"], r["target"])
                for r in records
            ]
    finally:
        driver.close()

    # Match words from the question
    words = set(re.findall(r"[a-z0-9]+", question.lower()))
    words -= {
        "what", "which", "who", "where", "when",
        "why", "how", "does", "do", "is", "are",
        "the", "a", "an", "in", "of", "for",
        "to", "and", "spotify"
    }

    matches = [
        (source, relation, target)
        for source, relation, target in relationships
        if any(
            word in re.findall(r"[a-z0-9]+", source.lower())
            or word in re.findall(r"[a-z0-9]+", target.lower())
            for word in words
        )
    ]

    return "\n".join(
        f"{source} {relation} {target}"
        for source, relation, target in matches[:30]
    )


# Step 4: Retrieve both sources in parallel
with ThreadPoolExecutor(max_workers=2) as executor:
    faiss_future = executor.submit(search_faiss)
    graph_future = executor.submit(search_graph)

    pdf_context = faiss_future.result()
    graph_context = graph_future.result()

# Step 5: Generate the final answer
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

prompt = f"""
You are answering questions about Spotify web app architecture.

Answer using ONLY the information below.
Combine the PDF context and Neo4j relationships.
Do not invent information.

If the provided context does not contain enough
information to answer the question, respond:
"I'm sorry, I don't have enough information to answer
this question. Please try asking something related
to the available Spotify architecture information."

Do not guess or generate unsupported information.

PDF Context:
{pdf_context}

Knowledge Graph:
{graph_context}

Question:
{question}
"""

response = llm.invoke(prompt)

print("\nHYBRID RAG ANSWER:\n")
print(response.content)
