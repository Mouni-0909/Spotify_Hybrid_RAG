
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Load credentials from .env
load_dotenv()

# Connect to Neo4j AuraDB
driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(
        os.getenv("NEO4J_USERNAME"),
        os.getenv("NEO4J_PASSWORD")
    )
)

# Verify connection
try:
    driver.verify_connectivity()
    print("Neo4j AuraDB Connected Successfully!")
finally:
    driver.close()
