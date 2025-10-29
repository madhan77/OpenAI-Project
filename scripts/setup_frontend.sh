#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<USAGE
Usage: $(basename "$0") [options]

Options:
  --skip-install   Skip running npm install
  --start          Start the Vite dev server after setup completes
  -h, --help       Show this help message
USAGE
}

SKIP_INSTALL=false
START_SERVER=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-install)
      SKIP_INSTALL=true
      shift
      ;;
    --start)
      START_SERVER=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

if [[ ! -d "$FRONTEND_DIR" ]]; then
  echo "Error: frontend directory not found at $FRONTEND_DIR" >&2
  exit 1
fi

if [[ ! -f "$FRONTEND_DIR/package.json" ]]; then
  echo "Error: package.json not found in $FRONTEND_DIR. Did you pull the frontend code?" >&2
  exit 1
fi

pushd "$FRONTEND_DIR" >/dev/null

if [[ "$SKIP_INSTALL" == false ]]; then
  echo "Installing npm dependencies..."
  npm install
else
  echo "Skipping dependency installation as requested."
fi

if [[ ! -f .env ]]; then
  echo "Creating .env from .env.example..."
  cp .env.example .env
  CREATED_ENV=true
else
  CREATED_ENV=false
fi

echo "\n✔ Frontend workspace is ready."

if [[ "$CREATED_ENV" == true ]]; then
  echo "A fresh .env file has been created. Update the following values with your Firebase credentials:"
else
  echo "Review your existing .env file and ensure the following Firebase values are populated:"
fi

echo "  - VITE_GRAPHQL_URL (only change this if your backend is not on http://localhost:4000/graphql)"
cat <<'ENV_VARS'
  - VITE_FIREBASE_API_KEY
  - VITE_FIREBASE_AUTH_DOMAIN
  - VITE_FIREBASE_PROJECT_ID
  - VITE_FIREBASE_APP_ID
  - Optional: VITE_FIREBASE_STORAGE_BUCKET, VITE_FIREBASE_MESSAGING_SENDER_ID, VITE_FIREBASE_MEASUREMENT_ID
ENV_VARS

echo "Once the values are set, start the dev server with:"
echo "  cd $FRONTEND_DIR && npm run dev"

if [[ "$START_SERVER" == true ]]; then
  echo "\nLaunching npm run dev..."
  npm run dev
fi

popd >/dev/null
