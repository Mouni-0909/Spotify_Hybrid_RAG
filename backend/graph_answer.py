
from pathlib import Path
from dotenv import load_dotenv
from neo4j import GraphDatabase
from langchain_openai import ChatOpenAI
import os
import re

# Step 1: Load credentials
folder = Path(__file__).resolve().parent.parent
load_dotenv(folder / ".env")

# Step 2: Ask a question
question = input("Enter your question: ").strip()

# Step 3: Connect to Neo4j
driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(
        os.getenv("NEO4J_USERNAME"),
        os.getenv("NEO4J_PASSWORD")
    )
)

# Step 4: Retrieve matching graph relationships
with driver.session() as session:

    # Automatically extracted graph
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

    # Existing manually created graph
    manual = session.run("""
        MATCH (a:Technology)-[r]->(b:Component)
        RETURN a.name AS source,
               type(r) AS relation,
               b.name AS target
    """)

    relationships += [
        (r["source"], r["relation"], r["target"])
        for r in manual
    ]

driver.close()

# Step 5: Find relevant relationships
words = set(re.findall(r"[a-z0-9]+", question.lower()))
stop_words = {
    "what", "which", "who", "where", "when", "why",
    "how", "does", "do", "is", "are", "the", "a",
    "an", "in", "of", "for", "to", "and", "spotify"
}

words -= stop_words

matches = [
    (source, relation, target)
    for source, relation, target in relationships
    if any(
        word in re.findall(r"[a-z0-9]+", source.lower())
        or word in re.findall(r"[a-z0-9]+", target.lower())
        for word in words
    )
]

# Step 6: Generate answer
if not matches:
    print("\nNo matching relationships found in Neo4j.")

else:
    context = "\n".join(
        f"{source} {relation} {target}"
        for source, relation, target in matches[:40]
    )

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0
    )

    prompt = f"""
    You are answering questions about a Spotify-style
    web application architecture.

    Answer using ONLY the Neo4j relationships below.
    Do not invent information.

    If the relationships do not contain the answer,
    say: The information is not available in the graph.

    Relationships:
    {context}

    Question:
    {question}
    """

    response = llm.invoke(prompt)

    print("\nNEO4J GRAPH RAG ANSWER:\n")
    print(response.content)
