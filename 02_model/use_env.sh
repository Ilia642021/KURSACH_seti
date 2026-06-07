#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# OMNeT++'s setenv scripts are not always compatible with "nounset" (-u).
set +u
source "${ROOT_DIR}/omnetpp-6.0.3/setenv"
source "${ROOT_DIR}/inet4.5/setenv"
set -u

echo "OMNeT++ and INET environment is active."
