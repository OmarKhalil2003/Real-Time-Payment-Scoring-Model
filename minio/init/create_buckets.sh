#!/usr/bin/env bash
set -euo pipefail

echo "Waiting for MinIO..."
until (/usr/bin/mc alias set local "http://minio:9000" "${MINIO_ROOT_USER}" "${MINIO_ROOT_PASSWORD}") >/dev/null 2>&1; do
  sleep 2
done

echo "Creating bucket: ${MINIO_BUCKET:-payments-lake}"
/usr/bin/mc mb --ignore-existing "local/${MINIO_BUCKET:-payments-lake}"

echo "Creating lake zones"
/usr/bin/mc mb --ignore-existing "local/${MINIO_BUCKET:-payments-lake}/raw"
/usr/bin/mc mb --ignore-existing "local/${MINIO_BUCKET:-payments-lake}/processed"
/usr/bin/mc mb --ignore-existing "local/${MINIO_BUCKET:-payments-lake}/curated"

echo "✅ MinIO bucket(s) initialized."

