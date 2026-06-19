from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


JsonDict = dict[str, Any]


class GraphNode(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str | None = None
    labels: list[str] = Field(default_factory=list)
    properties: JsonDict = Field(default_factory=dict)


class GraphRelationship(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str
    start_id: str | None = None
    end_id: str | None = None
    properties: JsonDict = Field(default_factory=dict)


class ReadyResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    neo4j: bool


class FoundResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    found: bool


class SystemOverviewResponse(FoundResponse):
    system: JsonDict = Field(default_factory=dict)
    report: JsonDict = Field(default_factory=dict)
    project: JsonDict = Field(default_factory=dict)


class SystemAssetsResponse(FoundResponse):
    system: JsonDict = Field(default_factory=dict)
    assets: dict[str, list[JsonDict]] = Field(default_factory=dict)


class CryptoProductsResponse(FoundResponse):
    system: JsonDict = Field(default_factory=dict)
    crypto_products: list[JsonDict] = Field(default_factory=list)


class ImportantDataResponse(FoundResponse):
    system: JsonDict = Field(default_factory=dict)
    important_data: list[JsonDict] = Field(default_factory=list)


class CryptoApplicationsResponse(FoundResponse):
    system: JsonDict = Field(default_factory=dict)
    crypto_applications: list[JsonDict] = Field(default_factory=list)


class DataProtectionGraph(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodes: list[GraphNode] = Field(default_factory=list)
    relationships: list[GraphRelationship] = Field(default_factory=list)


class DataProtectionResponse(FoundResponse):
    system: JsonDict = Field(default_factory=dict)
    data_protection: DataProtectionGraph = Field(default_factory=DataProtectionGraph)


class ReportFindingsResponse(FoundResponse):
    report: JsonDict = Field(default_factory=dict)
    findings: list[JsonDict] = Field(default_factory=list)
    evidences: list[JsonDict] = Field(default_factory=list)


class GenerationContextResponse(FoundResponse):
    report: JsonDict = Field(default_factory=dict)
    system: JsonDict = Field(default_factory=dict)
    assets: dict[str, list[JsonDict]] = Field(default_factory=dict)
    crypto_applications: list[JsonDict] = Field(default_factory=list)
    data_protection: DataProtectionGraph = Field(default_factory=DataProtectionGraph)
    findings: list[JsonDict] = Field(default_factory=list)
    evidences: list[JsonDict] = Field(default_factory=list)
    quality_flags: list[JsonDict] = Field(default_factory=list)


class EntitySearchResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str
    entities: list[JsonDict] = Field(default_factory=list)
