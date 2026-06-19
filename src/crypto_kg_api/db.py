from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from neo4j import Driver, GraphDatabase

from .config import Settings, get_settings

T = TypeVar("T")


class Neo4jClient:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._driver: Driver | None = None

    @property
    def driver(self) -> Driver:
        if self._driver is None:
            self._driver = GraphDatabase.driver(
                self.settings.neo4j_uri,
                auth=(self.settings.neo4j_username, self.settings.neo4j_password),
            )
        return self._driver

    def close(self) -> None:
        if self._driver is not None:
            self._driver.close()
            self._driver = None

    def verify_connectivity(self) -> None:
        self.driver.verify_connectivity()

    def execute_read(self, work: Callable[[Any], T]) -> T:
        with self.driver.session(database=self.settings.neo4j_database) as session:
            return session.execute_read(work)


_client: Neo4jClient | None = None


def get_client() -> Neo4jClient:
    global _client
    if _client is None:
        _client = Neo4jClient()
    return _client


def close_client() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None
