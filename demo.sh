#!/usr/bin/env bash
set -e

AGENT_URL="${AGENT_URL:-http://localhost:8000}"

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

usage() {
  echo ""
  echo -e "  ${BOLD}TE CUIDO — demo script${NC}"
  echo ""
  echo -e "  ${BOLD}Usage:${NC} ./demo.sh <event> [--watch]"
  echo ""
  echo -e "  ${BOLD}Events:${NC}"
  echo -e "    ${CYAN}fall${NC}      Simulate a fall (impact spike + immobility)"
  echo -e "    ${CYAN}low_hr${NC}    Simulate bradycardia (heart rate < 40 BPM)"
  echo -e "    ${CYAN}low_spo2${NC}  Simulate hypoxia (SpO2 < 90%)"
  echo -e "    ${CYAN}reset${NC}     Confirm patient wellbeing — cancels active alert"
  echo -e "    ${CYAN}status${NC}    Show current agent status"
  echo ""
  echo -e "  ${BOLD}Options:${NC}"
  echo -e "    ${CYAN}--watch${NC}   Poll /api/status every 3s after triggering"
  echo ""
  echo -e "  ${BOLD}Examples:${NC}"
  echo -e "    ${DIM}./demo.sh low_hr${NC}"
  echo -e "    ${DIM}./demo.sh fall --watch${NC}"
  echo -e "    ${DIM}./demo.sh reset${NC}"
  echo -e "    ${DIM}AGENT_URL=http://myserver:8000 ./demo.sh status${NC}"
  echo ""
}

status_line() {
  local data
  data=$(curl -sf "$AGENT_URL/api/status" 2>/dev/null) || { echo -e "${RED}agent offline${NC}"; return; }
  local s
  s=$(echo "$data" | python3 -c "import sys,json; print(json.load(sys.stdin)['status'])" 2>/dev/null)
  case "$s" in
    ok)        echo -e "${GREEN}● ok${NC}" ;;
    alert)     echo -e "${YELLOW}⚠  alert${NC}" ;;
    emergency) echo -e "${RED}🚨 emergency${NC}" ;;
    *)         echo -e "${DIM}unknown${NC}" ;;
  esac
}

print_json() {
  python3 -m json.tool 2>/dev/null || cat
}

EVENT="${1:-}"
WATCH=false
[[ "${2:-}" == "--watch" ]] && WATCH=true

if [[ -z "$EVENT" ]]; then
  usage; exit 1
fi

case "$EVENT" in
  fall|low_hr|low_spo2)
    DESCRIPTIONS=(
      [fall]="Simulating fall — impact spike + immobility"
      [low_hr]="Simulating bradycardia — heart rate below 40 BPM"
      [low_spo2]="Simulating hypoxia — SpO2 below 90%"
    )
    echo -e "\n${BOLD}${DESCRIPTIONS[$EVENT]:-Triggering $EVENT}${NC}\n"
    curl -s -X POST "$AGENT_URL/api/simulate?event_type=$EVENT" | print_json
    ;;
  reset)
    echo -e "\n${BOLD}Confirming patient wellbeing...${NC}\n"
    curl -s -X POST "$AGENT_URL/api/wellbeing" | print_json
    ;;
  status)
    echo -e "\n${BOLD}Agent status:${NC} $(status_line)\n"
    curl -sf "$AGENT_URL/api/status" | print_json
    ;;
  *)
    echo -e "\n${RED}Unknown event: $EVENT${NC}"
    usage; exit 1
    ;;
esac

if $WATCH; then
  echo -e "\n${CYAN}Watching status — Ctrl+C to stop${NC}\n"
  while true; do
    echo -e "$(date '+%H:%M:%S')  $(status_line)"
    sleep 3
  done
fi
