from neo4j import GraphDatabase
import os


def connect_to_neo4j():
    """Establishes a connection to the Neo4j database using environment variables."""
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USERNAME", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")
    return GraphDatabase.driver(uri, auth=(user, password))
