# Quick Start Guide - Trello Project Manager

## 🚀 Get Started in 5 Minutes

### Step 1: Get Your Trello Credentials (2 minutes)

1. Go to: https://trello.com/app-key
2. Copy your **API Key**
3. Click "Token" and authorize → Copy your **Token**
4. Open your Trello board → Copy **Board ID** from URL
   ```
   https://trello.com/b/ABC123XYZ/board-name
                        ^^^^^^^^^ This part
   ```

### Step 2: Set Up Environment (1 minute)

```bash
# Copy the template
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your favorite editor
```

Add:
```
TRELLO_API_KEY=your_key_from_step_1
TRELLO_TOKEN=your_token_from_step_1  
TRELLO_BOARD_ID=your_board_id_from_step_1
```

### Step 3: Install & Initialize (2 minutes)

```bash
# Install dependencies
pip install -r requirements.txt --break-system-packages

# Set up your board structure
python trello_setup.py

# Test it works
python trello_test.py
```

### Step 4: Start Using It! (Now!)

**In Claude Code:**

```python
from trello_manager import TrelloManager

manager = TrelloManager()

# See your board
print(manager.get_board_summary())

# Add a task
manager.create_card(
    list_name="Next Up",
    title="My first task",
    urgency="🟢",
    description="Testing the Trello integration!",
    labels=["Testing"]
)
```

**Or just ask the agent:**

```
"Show me my Trello board status"
"Add a new task: fix the login bug, urgent, backend issue"  
"Move the API integration task to In Progress"
```

## 📱 Voice Workflow Setup

### On Mobile:

1. Open Trello app
2. Open your board
3. Create a card using voice dictation:
   - "Urgent bug in payment system need to fix today"
   - "Update marketing homepage copy low priority"
   - "Build LinkedIn integration by Friday"

### In Claude Code:

```
"Process my voice notes from Trello and organize them"
```

The agent will:
- ✅ Parse natural language
- ✅ Detect urgency (urgent → 🔴)
- ✅ Assign labels (bug, backend, etc.)
- ✅ Extract due dates
- ✅ Create structured tasks
- ✅ Move to correct lists

## 🎯 Your First Session

Try this conversation:

**You**: "Show me my board status"

**Claude Code**: [Shows organized summary]

**You**: "Add a task: need to review the deployment pipeline, intermediate priority, deployment category"

**Claude Code**: ✅ Created: 🟠 Review Deployment Pipeline (Next Up) [Deployment]

**You**: "What should I work on next?"

**Claude Code**: [Analyzes In Progress and Next Up, suggests urgent tasks]

## 💡 Pro Tips

**Voice Capture:**
- Speak naturally - the agent is smart about parsing
- Include urgency words: "urgent", "ASAP", "low priority"
- Mention categories: "backend", "frontend", "bug"
- Say dates: "by Friday", "next week"

**Workflow:**
- Limit In Progress to 2-3 items
- Use To Review for quality gate
- Archive Completed items weekly
- Link documentation for complex tasks

**Urgency Guide:**
- 🔴 = Blocks the system from working
- 🟠 = Improves working functionality  
- 🟢 = Polish and nice-to-haves

## ⚡ Quick Commands

```python
from trello_manager import quick_add_task, get_board_status

# Quick add
quick_add_task("Fix auth bug", urgency="🔴", labels=["Bug"])

# Quick status
get_board_status()
```

## 🆘 Need Help?

**Board looks empty?**
→ Run `python trello_setup.py --samples` to add test cards

**Can't connect?**
→ Check your `.env` file has all three credentials

**Custom fields not working?**
→ Enable "Custom Fields" Power-Up in Trello

**Need more help?**
→ Check the full README.md

## 🎉 You're Ready!

You now have:
- ✅ Voice-driven task capture
- ✅ Intelligent auto-organization
- ✅ Full Kanban workflow
- ✅ Claude Code integration

Start dictating tasks and let Claude Code keep you organized! 🚀
