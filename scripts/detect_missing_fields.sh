#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/.env"
ENV_EXAMPLE="${ROOT_DIR}/.env.example"

if [[ ! -f "${ENV_FILE}" ]]; then
  cp "${ENV_EXAMPLE}" "${ENV_FILE}"
  echo "Created .env from .env.example."
fi

set -a
# shellcheck disable=SC1090
source "${ENV_FILE}"
set +a

container="${NEO4J_CONTAINER_NAME:-crypto-neo4j}"
username="${NEO4J_USERNAME:-neo4j}"
password="${NEO4J_PASSWORD:-crypto_neo4j_password}"

if ! docker exec "${container}" cypher-shell \
  -u "${username}" \
  -p "${password}" \
  "RETURN 1;" >/dev/null 2>&1; then
  echo "Neo4j is not ready. Start it with: scripts/neo4j.sh up" >&2
  exit 1
fi

echo "Applying ontology/detect_missing_fields.cypher ..."
docker exec -i "${container}" cypher-shell \
  -u "${username}" \
  -p "${password}" \
  < "${ROOT_DIR}/ontology/detect_missing_fields.cypher"

echo "Missing field detection completed."
