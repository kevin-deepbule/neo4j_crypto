from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from typing import Annotated, Any

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query
from neo4j.exceptions import Neo4jError, ServiceUnavailable

from .db import close_client, get_client
from .models import (
    CryptoApplicationsResponse,
    CryptoProductsResponse,
    DataProtectionResponse,
    EntitySearchResponse,
    GenerationContextResponse,
    ImportantDataResponse,
    ReadyResponse,
    ReportFindingsResponse,
    SystemAssetsResponse,
    SystemOverviewResponse,
)
from .queries import KnowledgeGraphQueries

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    yield
    close_client()


app = FastAPI(
    title="Crypto Neo4j Knowledge Graph API",
    version="0.1.0",
    description="Query API for crypto assessment report knowledge graphs.",
    lifespan=lifespan,
)


def get_query_service() -> KnowledgeGraphQueries:
    return KnowledgeGraphQueries(get_client())


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/ready", response_model=ReadyResponse)
def ready() -> ReadyResponse:
    try:
        get_client().verify_connectivity()
    except (Neo4jError, ServiceUnavailable) as exc:
        raise HTTPException(status_code=503, detail="Neo4j is not reachable") from exc
    return ReadyResponse(status="ready", neo4j=True)


def _run_query(operation: Callable[[], Any]) -> Any:
    try:
        return operation()
    except (Neo4jError, ServiceUnavailable) as exc:
        raise HTTPException(status_code=503, detail="Neo4j query failed") from exc


@app.get("/api/v1/systems/{system_id}/overview", response_model=SystemOverviewResponse)
def system_overview(
    system_id: str,
    service: KnowledgeGraphQueries = Depends(get_query_service),
) -> dict[str, Any]:
    return _run_query(lambda: service.system_overview(system_id))


@app.get("/api/v1/systems/{system_id}/assets", response_model=SystemAssetsResponse)
def system_assets(
    system_id: str,
    service: KnowledgeGraphQueries = Depends(get_query_service),
) -> dict[str, Any]:
    return _run_query(lambda: service.system_assets(system_id))


@app.get("/api/v1/systems/{system_id}/crypto-products", response_model=CryptoProductsResponse)
def crypto_products(
    system_id: str,
    service: KnowledgeGraphQueries = Depends(get_query_service),
) -> dict[str, Any]:
    return _run_query(lambda: service.crypto_products(system_id))


@app.get("/api/v1/systems/{system_id}/important-data", response_model=ImportantDataResponse)
def important_data(
    system_id: str,
    service: KnowledgeGraphQueries = Depends(get_query_service),
) -> dict[str, Any]:
    return _run_query(lambda: service.important_data(system_id))


@app.get("/api/v1/systems/{system_id}/crypto-applications", response_model=CryptoApplicationsResponse)
def crypto_applications(
    system_id: str,
    service: KnowledgeGraphQueries = Depends(get_query_service),
) -> dict[str, Any]:
    return _run_query(lambda: service.crypto_applications(system_id))


@app.get("/api/v1/systems/{system_id}/data-protection", response_model=DataProtectionResponse)
def data_protection(
    system_id: str,
    service: KnowledgeGraphQueries = Depends(get_query_service),
) -> dict[str, Any]:
    return _run_query(lambda: service.data_protection(system_id))


@app.get("/api/v1/reports/{report_id}/findings", response_model=ReportFindingsResponse)
def report_findings(
    report_id: str,
    service: KnowledgeGraphQueries = Depends(get_query_service),
) -> dict[str, Any]:
    return _run_query(lambda: service.report_findings(report_id))


@app.get("/api/v1/reports/{report_id}/generation-context", response_model=GenerationContextResponse)
def generation_context(
    report_id: str,
    service: KnowledgeGraphQueries = Depends(get_query_service),
) -> dict[str, Any]:
    return _run_query(lambda: service.generation_context(report_id))


@app.get("/api/v1/search/entities", response_model=EntitySearchResponse)
def search_entities(
    q: Annotated[str, Query(min_length=1)],
    service: KnowledgeGraphQueries = Depends(get_query_service),
) -> dict[str, Any]:
    return _run_query(lambda: service.search_entities(q))
