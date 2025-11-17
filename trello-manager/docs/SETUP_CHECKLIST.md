# Setup Checklist - Trello Project Manager

Use this checklist to ensure you've completed all setup steps correctly.

## ☑️ Pre-Setup (5 minutes)

- [ ] Have a Trello account
- [ ] Have Claude Code installed
- [ ] Have Python 3.x installed
- [ ] Have access to terminal/command line

## ☑️ Step 1: Get Trello Credentials (2 minutes)

- [ ] Visit https://trello.com/app-key
- [ ] Copy your API Key
- [ ] Generate and copy your Token (click the Token link)
- [ ] Create or open your project board in Trello
- [ ] Copy Board ID from URL (trello.com/b/BOARD_ID/board-name)
- [ ] **Verify**: You have all three credentials written down

## ☑️ Step 2: Download & Configure (2 minutes)

- [ ] Download all files from Claude Code outputs
- [ ] Create a project directory (e.g., `~/trello-manager/`)
- [ ] Move all files to this directory
- [ ] Copy `.env.example` to `.env`
- [ ] Edit `.env` file with your credentials:
  - [ ] TRELLO_API_KEY=your_actual_key
  - [ ] TRELLO_TOKEN=your_actual_token
  - [ ] TRELLO_BOARD_ID=your_actual_board_id
- [ ] **Verify**: `.env` file has all three values (no "your_" placeholders)

## ☑️ Step 3: Install Dependencies (1 minute)

```bash
cd ~/trello-manager/  # or your directory
pip install -r requirements.txt --break-system-packages
```

- [ ] Command completed without errors
- [ ] `requests` installed
- [ ] `python-dotenv` installed
- [ ] **Verify**: Run `pip list | grep requests` shows installed

## ☑️ Step 4: Initialize Board (2 minutes)

```bash
python trello_setup.py
```

Expected output:
- [ ] ✅ "Trello connection successful"
- [ ] ✅ Lists created (7 total)
- [ ] ✅ Urgency labels created (3 total)
- [ ] ✅ Category labels created (8 total)
- [ ] ✅ Custom field created (Documentation)
- [ ] ✅ "SETUP COMPLETE" message shown

**If you see warnings about Custom Fields:**
- [ ] Open your Trello board
- [ ] Click "Power-Ups" in menu
- [ ] Search for "Custom Fields"
- [ ] Click "Add"
- [ ] Re-run `python trello_setup.py`

## ☑️ Step 5: Test Integration (2 minutes)

```bash
python trello_test.py
```

Expected to pass:
- [ ] ✅ Connection test
- [ ] ✅ Lists test (shows 7 lists)
- [ ] ✅ Labels test (shows 11 labels)
- [ ] ✅ Card creation test
- [ ] ✅ Card movement test
- [ ] ✅ Card update test
- [ ] ✅ Board summary test
- [ ] "TEST SUITE COMPLETE" shown

When prompted:
- [ ] Archive test card (y/n - your choice)

**Verify in Trello:**
- [ ] Open your board in browser
- [ ] See test card (if not archived)
- [ ] See all 7 lists
- [ ] See labels (Red/Orange/Green urgency + categories)

## ☑️ Step 6: Test Basic Python Usage (2 minutes)

```bash
python
```

Then in Python:
```python
from trello_manager import TrelloManager
manager = TrelloManager()
print(manager.get_board_summary())
```

- [ ] No import errors
- [ ] Board summary displays
- [ ] Shows all your lists
- [ ] Shows any existing cards
- [ ] Exit with `exit()`

## ☑️ Step 7: Set Up Claude Code Agent (Optional, 2 minutes)

If using Claude Code agents feature:

```bash
# Copy agent to Claude Code agents directory
mkdir -p ~/.claude-code/agents/
cp trello-project-manager.md ~/.claude-code/agents/
```

- [ ] Agent file copied
- [ ] File readable in agents directory

**Or** just reference the prompt manually in your Claude Code sessions.

## ☑️ Step 8: First Real Task (1 minute)

### Option A: Direct Python
```python
from trello_manager import TrelloManager
manager = TrelloManager()

manager.create_card(
    list_name="Backlog",
    title="Set up Trello integration",
    urgency="🟢",
    description="Successfully configured Trello project manager!",
    labels=["Testing"]
)

print(manager.get_board_summary())
```

- [ ] Card created successfully
- [ ] Appears in Backlog list
- [ ] Has green urgency emoji
- [ ] Has Testing label

### Option B: Via Mobile
- [ ] Open Trello app on phone
- [ ] Navigate to your board
- [ ] Create a new card
- [ ] Use voice dictation: "Test task from mobile voice"
- [ ] Card appears in Trello

## ☑️ Step 9: Test Voice Processing (2 minutes)

In Claude Code session:
```python
from trello_manager import TrelloManager

manager = TrelloManager()

# If you created a mobile voice card, get it
cards = manager.get_all_cards()
print(f"Found {sum(len(c) for c in cards.values())} total cards")

# Create a test voice-style card
manager.create_card(
    list_name="Backlog",
    title="Raw voice note - urgent bug in system",
    description="This simulates what you'd dictate",
    labels=[]  # No labels yet - agent will add them
)
```

Then tell the agent:
"Look at the 'urgent bug in system' card and properly organize it with correct urgency and labels"

- [ ] Agent identifies urgency (should be 🔴)
- [ ] Agent adds appropriate labels (Bug, etc.)
- [ ] Agent moves to correct list (likely Next Up)
- [ ] Card is properly structured

## ☑️ Step 10: Verify Mobile → Claude Code Workflow (5 minutes)

Complete end-to-end test:

1. **On Mobile:**
   - [ ] Open Trello app
   - [ ] Create card with voice dictation
   - [ ] Say something like: "Need to review the deployment pipeline, medium priority, deployment stuff"

2. **On Desktop (Claude Code):**
   ```python
   from trello_manager import TrelloManager
   manager = TrelloManager()
   print(manager.get_board_summary())
   ```
   - [ ] See your voice note card
   
3. **Process with Agent:**
   "Process that deployment card I just added"
   
   - [ ] Agent reads current board
   - [ ] Agent identifies the card
   - [ ] Agent structures it properly
   - [ ] Agent assigns urgency (should be 🟠)
   - [ ] Agent adds Deployment label
   - [ ] Agent moves to appropriate list

4. **Verify in Trello:**
   - [ ] Open board in browser
   - [ ] See properly formatted card
   - [ ] Has urgency emoji
   - [ ] Has correct label
   - [ ] In correct list

## ✅ Final Verification

You're fully set up when:

- [ ] ✅ `.env` file configured with real credentials
- [ ] ✅ All dependencies installed
- [ ] ✅ Board initialized with lists and labels
- [ ] ✅ Test script passes all checks
- [ ] ✅ Python imports work (`from trello_manager import TrelloManager`)
- [ ] ✅ Can create cards via Python
- [ ] ✅ Can create cards via mobile
- [ ] ✅ Agent can process and organize cards
- [ ] ✅ Changes reflect in Trello immediately
- [ ] ✅ Board summary displays correctly

## 🎉 You're Ready!

If all boxes are checked, you can now:

✅ **Dictate tasks** on your phone into Trello  
✅ **Process with Claude Code** to auto-organize  
✅ **Manage workflow** through proper Kanban stages  
✅ **Track progress** with urgency and labels  
✅ **Maintain context** with documentation links  

## 🆘 Troubleshooting

**Import errors?**
→ Re-run: `pip install -r requirements.txt --break-system-packages`

**Connection failures?**
→ Check `.env` file has correct credentials (no spaces, no quotes)

**Lists not found?**
→ Re-run: `python trello_setup.py`

**Custom fields not working?**
→ Enable "Custom Fields" Power-Up in Trello board settings

**Can't find agent?**
→ Just use the prompt from `trello-project-manager.md` directly in sessions

**Still stuck?**
→ Check the README.md troubleshooting section

## 📚 Next Steps

Once setup is complete:

1. **Read QUICKSTART.md** for usage patterns
2. **Review README.md** for comprehensive reference
3. **Check ARCHITECTURE.md** for system understanding
4. **Try the examples** in the documentation
5. **Start dictating** real tasks!

## 🎯 Success Criteria

Your system is working correctly when:

- Voice dictation → Trello card creation works smoothly
- Claude Code can read your board state
- Agent organizes cards intelligently
- Urgency levels are applied correctly
- Labels are assigned appropriately  
- Tasks move through workflow stages
- Board stays clean and organized

---

**Estimated Total Setup Time**: 15-20 minutes  
**Difficulty Level**: Beginner-friendly  
**Support**: All docs included in delivery

Happy task managing! 🚀
