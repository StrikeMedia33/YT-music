#!/bin/bash
# Trello Manager Script Runner
# Usage: ./run_trello.sh <command>

cd "$(dirname "$0")"
source .venv/bin/activate

case "$1" in
    "summary")
        python3 -c "from trello_manager import TrelloManager; tm = TrelloManager(); print(tm.get_board_summary())"
        ;;
    "voice-notes")
        python3 -c "from trello_manager import TrelloManager; tm = TrelloManager(); notes = tm.get_cards_in_list('Voice Notes'); print(f'Voice Notes: {len(notes)} cards')"
        ;;
    "next-up")
        python3 -c "from trello_manager import TrelloManager; tm = TrelloManager(); cards = tm.get_cards_in_list('Next Up'); print(f'Next Up: {len(cards)} cards'); [print(f\"  - {c['name']}\") for c in cards]"
        ;;
    "test")
        python3 -c "from trello_manager import TrelloManager; tm = TrelloManager(); print(f'✅ Connected to board: {tm.board_id}')"
        ;;
    *)
        python3 "$@"
        ;;
esac
