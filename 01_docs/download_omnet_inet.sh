#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOWNLOAD_DIR="$ROOT_DIR/01_docs/downloads"
mkdir -p "$DOWNLOAD_DIR"

echo "Download dir: $DOWNLOAD_DIR"

OMNET_URL="https://github.com/omnetpp/omnetpp/releases/download/omnetpp-6.0.3/omnetpp-6.0.3-linux-x86_64.tgz"
INET_URL="https://github.com/inet-framework/inet/releases/download/v4.5.4/inet-4.5.4-src.tgz"

echo "[1/2] Downloading OMNeT++..."
curl -fL "$OMNET_URL" -o "$DOWNLOAD_DIR/omnetpp-6.0.3-linux-x86_64.tgz"

echo "[2/2] Downloading INET..."
curl -fL "$INET_URL" -o "$DOWNLOAD_DIR/inet-4.5.4-src.tgz"

echo "Done."
ls -lh "$DOWNLOAD_DIR"
