"""
Trello Board Setup Script
Run this once to initialize your board with proper lists, labels, and custom fields
"""

import os
from trello_manager import TrelloManager
from dotenv import load_dotenv

load_dotenv()

def setup_board():
    """Initialize Trello board with required structure"""
    
    manager = TrelloManager()
    print("🚀 Starting Trello Board Setup...")
    print(f"Board ID: {manager.board_id}\n")
    
    # ============================================================================
    # STEP 1: CREATE LISTS IN ORDER
    # ============================================================================
    
    print("📋 Setting up Lists...")
    
    required_lists = [
        "Voice Notes",
        "Backlog",
        "Planned",
        "Next Up",
        "In Progress",
        "To Review",
        "Completed",
        "Archive"
    ]
    
    existing_lists = manager.get_lists(force_refresh=True)
    
    for list_name in required_lists:
        if list_name not in existing_lists:
            try:
                data = {
                    'name': list_name,
                    'idBoard': manager.board_id,
                    'pos': 'bottom'  # Add to end
                }
                result = manager._make_request('POST', '/lists', data=data)
                print(f"  ✅ Created list: {list_name}")
                existing_lists[list_name] = result['id']
            except Exception as e:
                print(f"  ⚠️  Could not create list '{list_name}': {e}")
        else:
            print(f"  ✓ List already exists: {list_name}")
    
    # ============================================================================
    # STEP 2: CREATE URGENCY LABELS
    # ============================================================================
    
    print("\n🏷️  Setting up Urgency Labels...")
    
    urgency_labels = [
        {"name": "Urgent", "color": "red"},
        {"name": "Intermediate", "color": "orange"},
        {"name": "Not Urgent", "color": "green"}
    ]
    
    existing_labels = manager.get_labels(force_refresh=True)
    
    for label_config in urgency_labels:
        if label_config['name'] not in existing_labels:
            try:
                data = {
                    'name': label_config['name'],
                    'color': label_config['color'],
                    'idBoard': manager.board_id
                }
                manager._make_request('POST', '/labels', data=data)
                print(f"  ✅ Created label: {label_config['name']} ({label_config['color']})")
            except Exception as e:
                print(f"  ⚠️  Could not create label '{label_config['name']}': {e}")
        else:
            print(f"  ✓ Label already exists: {label_config['name']}")
    
    # ============================================================================
    # STEP 3: CREATE CATEGORY LABELS
    # ============================================================================
    
    print("\n🏷️  Setting up Category Labels...")
    
    category_labels = [
        {"name": "Agent Development", "color": "blue"},
        {"name": "Integration", "color": "purple"},
        {"name": "Frontend", "color": "yellow"},
        {"name": "Backend", "color": "pink"},
        {"name": "Testing", "color": "lime"},
        {"name": "Bug", "color": "red"},
        {"name": "Documentation", "color": "sky"},
        {"name": "Deployment", "color": "black"}
    ]
    
    existing_labels = manager.get_labels(force_refresh=True)
    
    for label_config in category_labels:
        if label_config['name'] not in existing_labels:
            try:
                data = {
                    'name': label_config['name'],
                    'color': label_config['color'],
                    'idBoard': manager.board_id
                }
                manager._make_request('POST', '/labels', data=data)
                print(f"  ✅ Created label: {label_config['name']} ({label_config['color']})")
            except Exception as e:
                print(f"  ⚠️  Could not create label '{label_config['name']}': {e}")
        else:
            print(f"  ✓ Label already exists: {label_config['name']}")
    
    # ============================================================================
    # STEP 4: CREATE CUSTOM FIELD FOR DOCUMENTATION
    # ============================================================================
    
    print("\n📝 Setting up Custom Fields...")
    
    existing_fields = manager.get_custom_fields(force_refresh=True)
    
    if "Documentation" not in existing_fields:
        try:
            data = {
                'idModel': manager.board_id,
                'modelType': 'board',
                'name': 'Documentation',
                'type': 'text',
                'pos': 'bottom',
                'display_cardFront': True
            }
            result = manager._make_request('POST', '/customFields', data=data)
            print(f"  ✅ Created custom field: Documentation")
        except Exception as e:
            print(f"  ⚠️  Could not create custom field 'Documentation': {e}")
            print(f"     You may need to enable Custom Fields Power-Up on your board first")
    else:
        print(f"  ✓ Custom field already exists: Documentation")
    
    # ============================================================================
    # STEP 5: VERIFY SETUP
    # ============================================================================
    
    print("\n" + "=" * 60)
    print("🎉 SETUP COMPLETE!")
    print("=" * 60)
    
    # Refresh caches
    lists = manager.get_lists(force_refresh=True)
    labels = manager.get_labels(force_refresh=True)
    fields = manager.get_custom_fields(force_refresh=True)
    
    print(f"\n✅ Lists ({len(lists)}):")
    for list_name in lists.keys():
        print(f"   - {list_name}")
    
    print(f"\n✅ Labels ({len(labels)}):")
    urgency_labels_list = []
    category_labels_list = []
    for label_name, label_info in labels.items():
        if label_name in ["Urgent", "Intermediate", "Not Urgent"]:
            urgency_labels_list.append(f"{label_name} ({label_info['color']})")
        else:
            category_labels_list.append(f"{label_name} ({label_info['color']})")
    
    if urgency_labels_list:
        print(f"   Urgency:")
        for label in urgency_labels_list:
            print(f"   - {label}")
    
    if category_labels_list:
        print(f"   Categories:")
        for label in category_labels_list:
            print(f"   - {label}")
    
    print(f"\n✅ Custom Fields ({len(fields)}):")
    for field_name in fields.keys():
        print(f"   - {field_name}")
    
    print("\n" + "=" * 60)
    print("📌 NEXT STEPS:")
    print("=" * 60)
    print("1. Verify your board structure at: https://trello.com")
    print("2. Enable 'Custom Fields' Power-Up if not already enabled")
    print("3. Test creating a card with: python trello_test.py")
    print("4. Start using your Trello Project Manager agent!")
    print("\n")


def create_sample_cards():
    """Create some sample cards to test the setup"""
    
    print("\n📝 Creating Sample Cards...")
    
    manager = TrelloManager()
    
    sample_cards = [
        {
            "list_name": "Video Ideas",
            "title": "Create 60-minute medieval fantasy ambience mix",
            "urgency": "🟢",
            "description": "20 unique tracks of medieval-themed background music with castle/fantasy visuals",
            "labels": ["Music Provider", "Visual Provider"]
        },
        {
            "list_name": "Planned",
            "title": "Implement Mubert API integration",
            "urgency": "🟠",
            "description": "Set up music provider to generate 20 unique tracks (3-4 mins each) with proper licensing",
            "labels": ["Music Provider", "Pipeline"]
        },
        {
            "list_name": "Next Up",
            "title": "Test FFmpeg visual switching for curated album",
            "urgency": "🔴",
            "description": "Verify visual-audio pairing works correctly (Visual 1 with Track 1, etc.) for 20-track videos",
            "labels": ["FFmpeg", "Pipeline"],
            "documentation_link": "https://github.com/YT-Music/docs/ffmpeg-rendering"
        }
    ]
    
    for card_data in sample_cards:
        try:
            manager.create_card(**card_data)
        except Exception as e:
            print(f"  ⚠️  Error creating sample card: {e}")
    
    print("\n✅ Sample cards created! Check your Trello board.\n")


if __name__ == "__main__":
    import sys
    
    print("\n" + "=" * 60)
    print("TRELLO BOARD SETUP")
    print("=" * 60 + "\n")
    
    # Check for environment variables
    if not os.getenv('TRELLO_API_KEY') or not os.getenv('TRELLO_TOKEN') or not os.getenv('TRELLO_BOARD_ID'):
        print("❌ ERROR: Missing environment variables!")
        print("\nPlease create a .env file with:")
        print("  TRELLO_API_KEY=your_api_key")
        print("  TRELLO_TOKEN=your_token")
        print("  TRELLO_BOARD_ID=your_board_id")
        print("\nGet your credentials at: https://trello.com/app-key\n")
        sys.exit(1)
    
    # Run setup
    setup_board()
    
    # Ask if user wants sample cards
    if len(sys.argv) > 1 and sys.argv[1] == "--samples":
        create_sample_cards()
    else:
        print("\n💡 TIP: Run with --samples to create example cards:")
        print("   python trello_setup.py --samples\n")
