# Trello Integration for YT Music

This directory contains the Trello integration for managing video production tasks in the YT Music project.

## Quick Start Guide

### 1. Create Trello Board (2 minutes)

1. Go to https://trello.com
2. Create a new board named **"YT Music"**
3. Copy the Board ID from the URL: `https://trello.com/b/BOARD_ID/yt-music`
4. Save the BOARD_ID for the next step

### 2. Get API Credentials (2 minutes)

1. Visit https://trello.com/app-key
2. Copy your **API Key**
3. Click the **"Token"** link and authorize to get your **Token**
4. Save both for the next step

### 3. Configure Environment (1 minute)

```bash
# Copy the template
cp .env.template .env

# Edit .env and add your credentials:
# - TRELLO_API_KEY=your_actual_api_key
# - TRELLO_TOKEN=your_actual_token
# - TRELLO_BOARD_ID=your_actual_board_id
```

⚠️ **Important:** Never commit the `.env` file! It's already in `.gitignore`.

### 4. Set Up Python Environment (3 minutes)

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate  # macOS/Linux
# OR
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 5. Initialize Board (2 minutes)

```bash
# Run setup script to create all lists and labels
python trello_setup.py

# Optional: Add sample cards to see how it works
python trello_setup.py --samples
```

This creates:
- **12 workflow lists**: Voice Notes, Video Ideas, Backlog, Planned, Next Up, Music Generation, Visual Generation, Rendering, Ready for Export, To Review, Completed, Archive
- **Urgency labels**: Urgent (red), Intermediate (orange), Not Urgent (green)
- **Category labels**: Music Provider, Visual Provider, FFmpeg, YouTube, Pipeline, Bug, Enhancement, Documentation

### 6. Test Integration (2 minutes)

```bash
# Run test suite
python trello_test.py

# Or use the wrapper script
./run_trello.sh test

# Get board summary
./run_trello.sh summary
```

### 7. Verify in Claude Code

Start a Claude Code session and say:
```
"Check the YT Music Trello board and give me a summary"
```

The agent should automatically read the board and report on all lists and cards.

---

## Board Structure

### Workflow Lists (in production order):

```
Voice Notes (mobile dictation)
        ↓
Video Ideas → Backlog → Planned → Next Up
        ↓         ↓         ↓         ↓
   Music Generation ← Visual Generation ← Rendering
                ↓
         Ready for Export
                ↓
          To Review → Completed → Archive
```

### Urgency System (Traffic Lights):

- 🔴 **Urgent** - Critical bugs, production issues, blockers
- 🟠 **Intermediate** - Important enhancements, non-blocking bugs
- 🟢 **Not Urgent** - Future improvements, polish, nice-to-haves

**Format:** Add urgency emoji at START of card title:
- `🔴 Fix visual switching bug in renderer`
- `🟠 Implement Mubert API integration`
- `🟢 Update documentation for music providers`

### Category Labels:

- **Music Provider** (blue) - Mubert/Beatoven tasks
- **Visual Provider** (purple) - Leonardo/Gemini tasks
- **FFmpeg** (yellow) - Video rendering tasks
- **YouTube** (pink) - Upload/metadata tasks
- **Pipeline** (orange) - End-to-end workflow
- **Bug** (red) - Bug fixes
- **Enhancement** (green) - Feature improvements
- **Documentation** (sky) - Docs and guides

---

## Using the Integration

### Via Claude Code Agent

The `trello-project-manager` agent is automatically available in Claude Code:

**Automatic behaviors:**
- ✅ Checks Voice Notes at session start
- ✅ Processes voice notes into structured tasks
- ✅ Moves completed work to "To Review" (not "Completed")
- ✅ Adds 🤖 audit comments for all operations

**Common requests:**
- "Check the Trello board"
- "Add this to Next Up: Fix rendering bug"
- "Move the Mubert integration task to In Progress"
- "What's in Music Generation?"
- "Process my voice notes"

### Via Wrapper Script

```bash
# Get board summary
./run_trello.sh summary

# Test connection
./run_trello.sh test

# Run custom Python code
./run_trello.sh -c "from trello_manager import TrelloManager; tm = TrelloManager(); print(tm.get_lists())"
```

### Voice Notes Workflow

1. **On Mobile:** Open Trello app, create card in "Voice Notes" list, dictate:
   - "Urgent: Fix FFmpeg visual switching bug"
   - "New video idea: 60-minute medieval fantasy ambience"
   - "Implement Leonardo.ai integration for visuals"

2. **On Desktop:** Start Claude Code session
   - Agent automatically detects voice notes
   - Parses urgency, keywords, categories
   - Creates structured tasks in appropriate lists
   - Archives original voice notes
   - Reports what was processed

---

## File Structure

```
trello-manager/
├── .env                    # Your credentials (DO NOT COMMIT!)
├── .env.template           # Template for credentials
├── .venv/                  # Python virtual environment
├── requirements.txt        # Python dependencies
├── trello_manager.py       # Core API wrapper (696 lines)
├── trello_setup.py         # Board initialization script
├── trello_test.py          # Integration test suite
├── run_trello.sh           # Bash wrapper for venv
├── README.md               # This file
└── docs/                   # Additional documentation
    ├── ARCHITECTURE.md     # System design
    ├── QUICKSTART.md       # Quick reference
    ├── README.md           # Usage guide
    └── SETUP_CHECKLIST.md  # Verification checklist
```

---

## Customization

### Adding New Lists

Edit `trello_setup.py`:
```python
required_lists = [
    "Voice Notes",
    "Video Ideas",
    # Add your custom list here
    "My Custom List",
    # ...rest of lists
]
```

### Adding New Labels

Edit `trello_setup.py`:
```python
category_labels = [
    {"name": "My Custom Label", "color": "purple"},
    # ...rest of labels
]
```

### Updating Agent Behavior

Edit `/.claude/agents/trello-project-manager.md`:
- Update list determination logic
- Add new keywords for categorization
- Customize workflow rules

---

## Troubleshooting

### "Missing environment variables" error

- Check that `.env` file exists in `trello-manager/` directory
- Verify all three variables are set: `TRELLO_API_KEY`, `TRELLO_TOKEN`, `TRELLO_BOARD_ID`
- Make sure there are no extra spaces or quotes in the values

### "Connection refused" or API errors

- Verify your API key and token are correct
- Check that board ID matches your actual board
- Ensure you have internet connection
- Visit https://trello.com/app-key to regenerate credentials if needed

### Agent can't find the board

- Make sure the board exists in your Trello account
- Verify the BOARD_ID in `.env` matches the board URL
- Check that the wrapper script has execute permissions: `chmod +x run_trello.sh`

### Lists not created

- Ensure you ran `python trello_setup.py`
- Check that you have permissions on the board
- Try manually creating one list to verify board access

---

## Documentation

For more detailed information:
- **Architecture**: See `docs/ARCHITECTURE.md`
- **Quick Reference**: See `docs/QUICKSTART.md`
- **Full Usage Guide**: See `docs/README.md`
- **Setup Checklist**: See `docs/SETUP_CHECKLIST.md`

---

## Support

**Trello API Documentation:** https://developer.atlassian.com/cloud/trello/rest/

**Claude Code Agent Help:** Type `/help` in Claude Code

**Issues:** If something isn't working, check:
1. Environment variables are set correctly
2. Virtual environment is activated
3. Dependencies are installed
4. Board ID matches your actual board
5. API credentials haven't expired

---

**Estimated Setup Time:** ~15 minutes

**Board URL:** https://trello.com/b/YOUR_BOARD_ID/yt-music

Replace `YOUR_BOARD_ID` with your actual board ID once created.
