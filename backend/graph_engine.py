
from pathlib import Path
from dotenv import load_dotenv
from neo4j import GraphDatabase
import os

# Step 1: Load Neo4j credentials
folder = Path(__file__).resolve().parent.parent
load_dotenv(folder / ".env")

# Step 2: Connect to Neo4j AuraDB
driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(
        os.getenv("NEO4J_USERNAME"),
        os.getenv("NEO4J_PASSWORD")
    )
)

# Step 3: Spotify database relationships
relationships = [
    ("PostgreSQL", "STORES", "Users"),
    ("PostgreSQL", "STORES", "Playlists"),
    ("PostgreSQL", "STORES", "Subscriptions"),
    ("Redis", "CACHES", "Sessions"),
    ("Redis", "CACHES", "Playback State"),
    ("Elasticsearch", "INDEXES", "Tracks"),
    ("Elasticsearch", "INDEXES", "Artists"),
    ("Elasticsearch", "INDEXES", "Albums"),
    ("ClickHouse", "STORES", "Playback Events"),
    ("ClickHouse", "STORES", "Search Events"),
    ("S3", "STORES", "Audio Segments")
]

# Step 4: Add database relationships
with driver.session() as session:
    for technology, relation, component in relationships:
        session.run(
            f"""
            MERGE (a:Technology {{name: $technology}})
            MERGE (b:Component {{name: $component}})
            MERGE (a)-[:{relation}]->(b)
            """,
            technology=technology,
            component=component
        ).consume()

print("Spotify database relationships created!")
print("Total database relationships:", len(relationships))


# Step 5: Spotify microservice relationships
services = [
    ("Auth & Identity Service", "MANAGES", "User Login"),
    ("Auth & Identity Service", "MANAGES", "Sessions"),
    ("User Profile Service", "MANAGES", "User Profiles"),
    ("API Gateway", "HANDLES", "Authentication"),
    ("API Gateway", "HANDLES", "Rate Limiting"),
    ("Media Processor Service", "PROCESSES", "Media")
]

# Step 6: Add microservice relationships
with driver.session() as session:
    for service, relation, component in services:
        session.run(
            f"""
            MERGE (a:SpotifyService {{name: $service}})
            MERGE (b:SpotifyComponent {{name: $component}})
            MERGE (a)-[:{relation}]->(b)
            """,
            service=service,
            component=component
        ).consume()

print("Spotify microservice relationships created!")
print("Total microservice relationships:", len(services))

# Step 7: Close Neo4j connection
driver.close()

print("\nSpotify knowledge graph updated successfully!")
