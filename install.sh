#!/usr/bin/env bash
# Install dev-brain into one or more coding agents. See install.py --help.
#   ./install.sh                  every agent found on this machine
#   ./install.sh opencode codex   only those
set -eu
exec python3 "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)/install.py" "$@"
