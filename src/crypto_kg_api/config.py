from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str = "crypto_neo4j_password"
    neo4j_database: str = "neo4j"


def get_settings() -> Settings:
    return Settings(
        neo4j_uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        neo4j_username=os.getenv("NEO4J_USERNAME", "neo4j"),
        neo4j_password=os.getenv("NEO4J_PASSWORD", "crypto_neo4j_password"),
        neo4j_database=os.getenv("NEO4J_DATABASE", "neo4j"),
    )
