#!/usr/bin/env bash
set -euo pipefail

export TEST_X7_COMPOSE_FILES="${TEST_X7_COMPOSE_FILES:-docker-compose.yml:docker-compose.python313.yml}"
export TEST_X7_GATE_OUTPUT_DIR="${TEST_X7_GATE_OUTPUT_DIR:-user_data/backtest_results/test_x7_python313_80pair_gate}"

exec "$(dirname "$0")/run_80pair_5s_gate.sh"
