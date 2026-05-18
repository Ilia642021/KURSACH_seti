#!/usr/bin/env bash
set -euo pipefail

check_cmd() {
  local name="$1"
  if command -v "$name" >/dev/null 2>&1; then
    echo "OK: $name -> $(command -v "$name")"
  else
    echo "MISS: $name"
  fi
}

echo "=== Required tools check ==="
check_cmd omnetpp
check_cmd opp_run
check_cmd opp_env
check_cmd wireshark
check_cmd tshark
check_cmd cmake
check_cmd make
check_cmd gcc
check_cmd g++
check_cmd git
check_cmd python3
