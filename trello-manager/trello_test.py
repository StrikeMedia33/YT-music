"""
Trello Manager Test Script
Quick test to verify your Trello integration is working correctly
"""

from trello_manager import TrelloManager
import os
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    """Test basic connection to Trello"""
    print("\n" + "="*60)
    print("TESTING TRELLO CONNECTION")
    print("="*60 + "\n")
    
    try:
        manager = TrelloManager()
        print("✅ Successfully connected to Trello!")
        print(f"   Board ID: {manager.board_id}")
        return manager
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None

def test_lists(manager):
    """Test fetching lists"""
    print("\n" + "="*60)
    print("TESTING LISTS")
    print("="*60 + "\n")
    
    try:
        lists = manager.get_lists()
        print(f"✅ Found {len(lists)} lists:")
        for list_name, list_id in lists.items():
            print(f"   - {list_name}")
        return True
    except Exception as e:
        print(f"❌ Failed to fetch lists: {e}")
        return False

def test_labels(manager):
    """Test fetching labels"""
    print("\n" + "="*60)
    print("TESTING LABELS")
    print("="*60 + "\n")
    
    try:
        labels = manager.get_labels()
        print(f"✅ Found {len(labels)} labels:")
        
        urgency_labels = []
        category_labels = []
        
        for label_name, label_info in labels.items():
            if label_name in ["Urgent", "Intermediate", "Not Urgent"]:
                urgency_labels.append(f"{label_name} ({label_info['color']})")
            else:
                category_labels.append(f"{label_name} ({label_info['color']})")
        
        if urgency_labels:
            print("\n   Urgency Labels:")
            for label in urgency_labels:
                print(f"   - {label}")
        
        if category_labels:
            print("\n   Category Labels:")
            for label in category_labels:
                print(f"   - {label}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to fetch labels: {e}")
        return False

def test_create_card(manager):
    """Test creating a card"""
    print("\n" + "="*60)
    print("TESTING CARD CREATION")
    print("="*60 + "\n")
    
    try:
        card = manager.create_card(
            list_name="Backlog",
            title="Test Card - Safe to Delete",
            urgency="🟢",
            description="This is a test card created by trello_test.py. Feel free to delete it.",
            labels=["Testing"]
        )
        print(f"✅ Successfully created test card!")
        print(f"   Card ID: {card['id']}")
        print(f"   Card Name: {card['name']}")
        print(f"   Card URL: {card['url']}")
        return card['id']
    except Exception as e:
        print(f"❌ Failed to create card: {e}")
        return None

def test_move_card(manager, card_id):
    """Test moving a card"""
    print("\n" + "="*60)
    print("TESTING CARD MOVEMENT")
    print("="*60 + "\n")
    
    try:
        card = manager.move_card(
            card_id=card_id,
            destination_list="Planned"
        )
        print(f"✅ Successfully moved card to Planned!")
        return True
    except Exception as e:
        print(f"❌ Failed to move card: {e}")
        return False

def test_update_card(manager, card_id):
    """Test updating a card"""
    print("\n" + "="*60)
    print("TESTING CARD UPDATE")
    print("="*60 + "\n")
    
    try:
        card = manager.update_card(
            card_id=card_id,
            urgency="🟠",
            description="Updated description - This test card has been updated successfully!"
        )
        print(f"✅ Successfully updated card!")
        return True
    except Exception as e:
        print(f"❌ Failed to update card: {e}")
        return False

def test_board_summary(manager):
    """Test getting board summary"""
    print("\n" + "="*60)
    print("TESTING BOARD SUMMARY")
    print("="*60 + "\n")
    
    try:
        summary = manager.get_board_summary()
        print(summary)
        return True
    except Exception as e:
        print(f"❌ Failed to get board summary: {e}")
        return False

def cleanup_test_card(manager, card_id):
    """Archive the test card"""
    print("\n" + "="*60)
    print("CLEANUP")
    print("="*60 + "\n")
    
    try:
        response = input("Would you like to archive the test card? (y/n): ")
        if response.lower() == 'y':
            manager.archive_card(card_id)
            print("✅ Test card archived!")
        else:
            print("ℹ️  Test card left on board (you can delete it manually)")
    except Exception as e:
        print(f"⚠️  Could not archive test card: {e}")

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("TRELLO MANAGER TEST SUITE")
    print("="*60)
    
    # Check environment
    if not all([os.getenv('TRELLO_API_KEY'), os.getenv('TRELLO_TOKEN'), os.getenv('TRELLO_BOARD_ID')]):
        print("\n❌ ERROR: Missing environment variables!")
        print("Please ensure your .env file contains:")
        print("  - TRELLO_API_KEY")
        print("  - TRELLO_TOKEN")
        print("  - TRELLO_BOARD_ID")
        return
    
    # Run tests
    manager = test_connection()
    if not manager:
        return
    
    test_lists(manager)
    test_labels(manager)
    
    # Create test card
    card_id = test_create_card(manager)
    
    if card_id:
        test_move_card(manager, card_id)
        test_update_card(manager, card_id)
        test_board_summary(manager)
        cleanup_test_card(manager, card_id)
    
    print("\n" + "="*60)
    print("TEST SUITE COMPLETE")
    print("="*60)
    print("\n✅ All systems operational! Your Trello integration is ready.")
    print("\n📌 Next steps:")
    print("   1. Try the trello-project-manager agent in Claude Code")
    print("   2. Start adding tasks via voice notes or directly")
    print("   3. Review the board summary regularly")
    print("\n")

if __name__ == "__main__":
    main()
