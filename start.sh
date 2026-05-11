#!/usr/bin/env bash
set -e

if [ ! -f .env ]; then
  cp .env.example .env
  echo ""
  echo "  .env created from .env.example"
  echo "  Open .env, fill in your API keys, then run ./start.sh again."
  echo ""
  exit 1
fi

docker compose up --build "$@"
