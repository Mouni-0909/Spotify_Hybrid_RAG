
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

NO_ANSWER = (
    "I'm sorry, I don't have enough information to answer "
    "this question. Please try asking something related "
    "to the available Spotify architecture information."
)

# Step 2: Search PDF using FAISS
def search_faiss(question):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    db = FAISS.load_local(
        str(folder / "faiss_index"),
        embeddings,
        allow_dangerous_deserialization=True
    )

    docs = db.similarity_search(question, k=4)
    return "\n\n".join(doc.page_content for doc in docs)


# Step 3: Search Neo4j Knowledge Graph
def search_graph(question):
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
    finally: driver.close()
     # Understand common database-related questions
    question_lower = question.lower()

    if "database" in question_lower and (
        "user" in question_lower or "information" in question_lower
    ):
        question = question + " PostgreSQL users profiles subscriptions"
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


# Step 4: Generate answer from selected context
def generate_answer(question, context):
    if not context.strip():
        return NO_ANSWER

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    prompt = f"""
    You are answering questions about Spotify web app architecture.

    Answer using ONLY the information below.
    Do not invent information.

    If the context does not contain enough information
    to answer the question, respond exactly:
    {NO_ANSWER}

    Context:
    {context}

    Question:
    {question}
    """

    return llm.invoke(prompt).content


# Step 5: Vector RAG - FAISS only
def get_vector_answer(question):
    if not question or not question.strip():
        return "Please enter a question."

    pdf_context = search_faiss(question)
    return generate_answer(question, pdf_context)


# Step 6: Graph RAG - Neo4j only
def get_graph_answer(question):
    if not question or not question.strip():
        return "Please enter a question."

    graph_context = search_graph(question)
    return generate_answer(question, graph_context)


# Step 7: Hybrid RAG - FAISS + Neo4j
def get_hybrid_answer(question):
    if not question or not question.strip():
        return "Please enter a question."

    with ThreadPoolExecutor(max_workers=2) as executor:
        faiss_future = executor.submit(search_faiss, question)
        graph_future = executor.submit(search_graph, question)

        pdf_context = faiss_future.result()
        graph_context = graph_future.result()

    context = f"""
    PDF Context:
    {pdf_context}

    Knowledge Graph:
    {graph_context}
    """

    return generate_answer(question, context)


# Step 8: Test from terminal
if __name__ == "__main__":
    question = input("Enter your question: ")

    print("\nVECTOR RAG ANSWER:\n")
    print(get_vector_answer(question))

    print("\nGRAPH RAG ANSWER:\n")
    print(get_graph_answer(question))

    print("\nHYBRID RAG ANSWER:\n")
    print(get_hybrid_answer(question))
