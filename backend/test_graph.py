
from pathlib import Path
from dotenv import load_dotenv
from neo4j import GraphDatabase
import os

# Step 1: Load credentials
folder = Path(__file__).resolve().parent.parent
load_dotenv(folder / ".env")

# Step 2: Connect to Neo4j
driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(
        os.getenv("NEO4J_USERNAME"),
        os.getenv("NEO4J_PASSWORD")
    )
)

# Step 3: Search graph relationships
question = "PostgreSQL"

with driver.session() as session:
    results = session.run("""
        MATCH (a:Technology {name: $name})-[r]->(b:Component)
        RETURN a.name AS technology,
               type(r) AS relation,
               b.name AS component
    """, name=question)

    for record in results:
        print(
            record["technology"],
            record["relation"],
            record["component"]
        )

driver.close()
