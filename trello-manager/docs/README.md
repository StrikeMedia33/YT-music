# Trello Project Manager for Claude Code

A powerful, voice-friendly task management system that integrates Trello with Claude Code for intelligent project organization.

## Overview

This system replaces Obsidian-based task tracking with Trello as the single source of truth, while maintaining the intelligent workflow management you're used to. Perfect for voice-driven task capture via mobile dictation directly into Trello.

## Features

✅ **Voice-First Workflow**: Dictate tasks on mobile → Auto-organized by Claude Code  
✅ **Traffic Light Urgency**: 🔴🟠🟢 visual priority system  
✅ **Smart Task Parsing**: Intelligent urgency and category detection  
✅ **Full Kanban Support**: 7-stage workflow (Backlog → Archive)  
✅ **Documentation Links**: Context preservation via custom fields  
✅ **Quality Gate**: "To Review" list for approval before completion  

## Project Structure

```
├── trello_manager.py          # Core Trello API integration
├── trello_setup.py             # One-time board initialization
├── trello_test.py              # Integration testing
├── trello-project-manager.md   # Claude Code agent prompt
├── .env.example                # Environment template
└── README.md                   # This file
```

## Quick Start

### 1. Get Trello Credentials

1. Visit https://trello.com/app-key
2. Copy your **API Key**
3. Click the "Token" link and authorize to get your **Token**
4. Create or choose a board and get its **Board ID** from the URL:
   ```
   https://trello.com/b/ABC123XYZ/my-board
                        ^^^^^^^^^ This is your Board ID
   ```

### 2. Configure Environment

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your credentials
TRELLO_API_KEY=your_api_key_here
TRELLO_TOKEN=your_token_here
TRELLO_BOARD_ID=your_board_id_here
```

### 3. Install Dependencies

```bash
pip install requests python-dotenv --break-system-packages
```

### 4. Initialize Your Board

```bash
# Set up lists, labels, and custom fields
python trello_setup.py

# Optional: Add sample cards to test
python trello_setup.py --samples
```

### 5. Test the Integration

```bash
python trello_test.py
```

This will verify:
- ✅ API connection
- ✅ Lists are accessible
- ✅ Labels are configured
- ✅ Card creation/updating works
- ✅ Board summary generation

### 6. Set Up Claude Code Agent

Copy `trello-project-manager.md` to your Claude Code agents directory:

```bash
# If using Claude Code agents feature
cp trello-project-manager.md ~/.claude-code/agents/
```

## Board Structure

### Lists

```
Backlog → Planned → Next Up → In Progress → To Review → Completed → Archive
```

- **Backlog**: Ideas and future features
- **Planned**: Scoped and prioritized tasks
- **Next Up**: Ready to work on immediately  
- **In Progress**: Currently active (limit 2-3)
- **To Review**: Awaiting approval
- **Completed**: Recently finished work
- **Archive**: Historical completed tasks

### Urgency System

**🔴 Red (Urgent)**
- Critical core functionality
- Production blockers
- Security issues

**🟠 Orange (Intermediate)**  
- Important enhancements
- UX/UI improvements
- Non-blocking bugs

**🟢 Green (Not Urgent)**
- Nice-to-have features
- Polish and refinements
- Future improvements

### Labels

**Urgency** (auto-applied):
- Urgent (red)
- Intermediate (orange)
- Not Urgent (green)

**Categories**:
- Agent Development
- Integration
- Frontend
- Backend
- Testing
- Bug
- Documentation
- Deployment

## Usage

### In Claude Code Sessions

```python
# Start your session
from trello_manager import TrelloManager

manager = TrelloManager()

# Get board overview
print(manager.get_board_summary())

# Add a new task
manager.create_card(
    list_name="Next Up",
    title="Fix API timeout issue",
    urgency="🔴",
    description="Users experiencing timeouts on webhook endpoints",
    labels=["Bug", "Backend"],
    due_date="15-11-2025"
)

# Move task through workflow
manager.move_card(card_id, "In Progress")
manager.move_card(card_id, "To Review")
manager.move_card(card_id, "Completed", mark_complete=True)
```

### Using the Agent

Just reference the agent in your Claude Code prompts:

```
"Hey, can you process my voice notes from Trello and organize them?"

"I finished the Facebook integration - update the project manager"

"Show me what's in In Progress and suggest what to work on next"

"Add a new task: urgent bug in payment flow, backend issue"
```

## Voice Notes Workflow

### Mobile Dictation → Trello

1. **On your phone**: Open Trello
2. **Create a card** in any list (or create a "Voice Notes" list)
3. **Use voice dictation** to describe the task naturally:
   - "Urgent bug in the API sync webhook, timing out on large payloads, backend stuff"
   - "Need to update the marketing copy on the homepage, low priority"
   - "Build LinkedIn integration with analytics by next Friday"

### Claude Code Processing

When you're ready to organize:

```python
from trello_manager import TrelloManager

manager = TrelloManager()

# Get your voice notes (from any list you dictated into)
notes = manager.get_cards_in_list("Your List Name")

# The agent will:
# 1. Parse natural language
# 2. Detect urgency (urgent/ASAP/critical → 🔴)
# 3. Identify categories (backend, API, bug → labels)
# 4. Extract due dates
# 5. Create properly formatted cards
# 6. Move to appropriate lists
```

## Advanced Features

### Search Across Board

```python
results = manager.search_cards("API integration")
for card in results:
    print(manager.format_card_summary(card))
```

### Bulk Operations

```python
# Get all cards in a list
cards = manager.get_cards_in_list("In Progress")

# Move multiple cards
for card in cards:
    if "testing complete" in card['desc'].lower():
        manager.move_card(card['id'], "To Review")
```

### Documentation Links

```python
manager.create_card(
    list_name="Next Up",
    title="Implement new agent architecture",
    urgency="🟠",
    documentation_link="https://docs.google.com/document/d/ABC123"
)
```

## API Reference

### TrelloManager Class

#### Card Operations

```python
# Create
manager.create_card(list_name, title, urgency, description, labels, due_date, documentation_link)

# Update  
manager.update_card(card_id, title, description, urgency, labels, due_date)

# Move
manager.move_card(card_id, destination_list, position, mark_complete)

# Archive
manager.archive_card(card_id)
```

#### Read Operations

```python
# Get cards
manager.get_cards_in_list(list_name)
manager.get_all_cards()
manager.search_cards(query)

# Get board overview
manager.get_board_summary()

# Format for display
manager.format_card_summary(card)
```

#### List & Label Operations

```python
# Lists
manager.get_lists()
manager.get_list_id(list_name)

# Labels  
manager.get_labels()
manager.get_label_ids(label_names)
```

#### Custom Fields

```python
manager.set_custom_field_value(card_id, "Documentation", url)
```

### Quick Helper Functions

```python
from trello_manager import quick_add_task, move_to_review, mark_complete, get_board_status

# Quick add
quick_add_task("Fix bug", urgency="🔴", labels=["Bug"])

# Quick move
move_to_review(card_id)
mark_complete(card_id)

# Quick status
get_board_status()
```

## Best Practices

### Task Writing

✅ **Good**: "Fix webhook timeout in API sync endpoint"  
❌ **Bad**: "Fix bug"

✅ **Good**: "Implement LinkedIn auto-posting with analytics tracking"  
❌ **Bad**: "LinkedIn stuff"

### Urgency Assessment

Ask: "Does this block the system from working?"
- Yes → 🔴 Urgent
- It improves working features → 🟠 Intermediate  
- It's polish/nice-to-have → 🟢 Not Urgent

### Workflow

1. **Capture** (voice notes or quick adds)
2. **Organize** (let Claude Code structure them)
3. **Plan** (move to Planned/Next Up)
4. **Execute** (In Progress, limit to 2-3)
5. **Review** (To Review for approval)
6. **Complete** (mark done, move to Completed)
7. **Archive** (weekly cleanup)

### Keep In Progress Focused

- Limit to 2-3 active items
- One per developer/agent
- Move to To Review when done, not straight to Completed

## Troubleshooting

### "Missing Trello credentials" Error

Check your `.env` file has all three values:
```bash
TRELLO_API_KEY=xxx
TRELLO_TOKEN=xxx
TRELLO_BOARD_ID=xxx
```

### "List not found" Error

Run the setup script again:
```bash
python trello_setup.py
```

### Custom Fields Not Working

Enable the "Custom Fields" Power-Up on your board:
1. Open your Trello board
2. Click "Power-Ups" in the menu
3. Search for "Custom Fields"
4. Click "Add"

### Rate Limiting

Trello API has rate limits (300 requests per 10 seconds). If you hit limits:
- Batch operations when possible
- Use the cached `get_lists()` and `get_labels()` methods
- Add small delays between bulk operations

## Integration with Claude Code

### Setting Up the Agent

The `trello-project-manager.md` file contains the full agent prompt. Claude Code will:

1. **Always read board state first** (prevents conflicts)
2. **Parse voice notes intelligently** (urgency, categories, dates)
3. **Apply best practices** (task structure, naming, organization)
4. **Maintain workflow** (proper list progression)
5. **Provide summaries** (clear status updates)

### Example Session

```
You: "Hey, I just dictated 3 new tasks into Trello. Can you organize them?"

Claude Code: 
📊 Current Board State:
  - Backlog: 5 cards
  - Voice Notes: 3 cards (unprocessed)

🔄 Processing Voice Notes...

✅ Processed: "urgent api bug timing out" 
   → 🔴 Fix API Timeout Bug (Next Up) [Backend, Bug]

✅ Processed: "update homepage copy low priority"
   → 🟢 Update Homepage Marketing Copy (Backlog) [Frontend]

✅ Processed: "linkedin integration by friday"
   → 🟠 Build LinkedIn Integration (Planned) [Integration]
   Due: 14-11-2025

📋 Updated Board State:
  - Backlog: 6 cards
  - Planned: 3 cards  
  - Next Up: 4 cards (1 urgent)
  - Voice Notes: 0 cards

⚠️  Urgent task detected in Next Up!
💡 Recommend starting: 🔴 Fix API Timeout Bug
```

## ScaleGrow Project Context

This system is optimized for managing:
- **AI Agent Development**: IngestAgent, SummariserAgent, etc.
- **Platform Integrations**: Facebook, Instagram, LinkedIn, X
- **Full-Stack Work**: Python backend + Next.js frontend
- **Deployment**: Render, Neon Postgres, environment management

Common labels and patterns are pre-configured for this workflow.

## Roadmap

Planned enhancements:
- [ ] Automated due date suggestions based on urgency
- [ ] Sprint planning helpers
- [ ] Dependency tracking between cards
- [ ] Time estimates and tracking
- [ ] Slack notifications for urgent tasks
- [ ] Weekly digest emails
- [ ] Voice-to-task with Claude's native audio API

## Support

**Issues?** Check the troubleshooting section above.

**Feature requests?** Add them to your Trello board with the "Documentation" label!

**Questions?** The `trello-project-manager` agent is designed to help with Trello operations during your Claude Code sessions.

## License

MIT - Feel free to adapt for your own projects!

---

Built with ❤️ for efficient, voice-driven project management.
