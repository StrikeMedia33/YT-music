"""
Move Phase 1 and Phase 2 cards to Next Up list
"""

import os
from trello_manager import TrelloManager
from dotenv import load_dotenv

load_dotenv()

def main():
    manager = TrelloManager()

    print("🚀 Moving Phase 1 and Phase 2 cards to 'Next Up'...\n")

    # Get all cards in Backlog
    lists = manager.get_lists()
    backlog_id = lists.get("Backlog")

    if not backlog_id:
        print("❌ Could not find Backlog list")
        return

    # Get all cards in Backlog
    response = manager._make_request('GET', f'/lists/{backlog_id}/cards')

    phase_1_2_cards = []
    for card in response:
        card_name = card.get('name', '')
        if 'Phase 1.' in card_name or 'Phase 2.' in card_name:
            phase_1_2_cards.append(card)

    print(f"Found {len(phase_1_2_cards)} Phase 1 & 2 cards to move\n")

    # Move each card to Next Up
    for card in phase_1_2_cards:
        card_title = card['name']
        try:
            manager.move_card(
                card_id=card['id'],
                destination_list="Next Up"
            )
            manager.add_comment(
                card_id=card['id'],
                comment=f"🎯 Moving to Next Up to start foundational work"
            )
            print(f"✅ Moved: {card_title}")
        except Exception as e:
            print(f"❌ Error moving {card_title}: {e}")

    print(f"\n✅ All Phase 1 & 2 tasks are now in 'Next Up'!")
    print("📋 Ready to start working on Phase 1.1\n")

if __name__ == "__main__":
    main()
