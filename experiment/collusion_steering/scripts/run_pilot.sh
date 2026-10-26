#!/usr/bin/env bash
# Convenience wrapper: set the CA bundle, then run the pilot.
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ -z "${SSL_CERT_FILE:-}" ]]; then
  export SSL_CERT_FILE="$(uv run python -c 'import certifi; print(certifi.where())')"
fi

exec uv run python run_experiment.py "$@"
